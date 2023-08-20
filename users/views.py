from __future__ import annotations

import logging
from base64 import urlsafe_b64decode
from datetime import datetime
from datetime import timedelta
from random import randrange

import requests
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count
from django.db.models import Sum
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode

from .decorators import user_not_authenticated
from .forms import ProductForm
from .forms import ProductUpdateForm
from .forms import ProductVariationForm
from .forms import RegistrationForm
from .forms import UserAddressForm
from .forms import UserProfileForm
from .models import Account
from .models import Address
from .models import Category
from .models import Product
from .models import ProductBannerImage
from .models import ProductImage
from .models import ProductVariation
from .utils import send_otp
from carts.models import Cart
from carts.models import CartItem
from carts.views import _cart_id
from offers.models import Offer
from orders.models import Order
from orders.models import OrderProduct


# email


def home(request):
    """
    Render the index page with product and banner image data.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML template for the index page.
    """
    products = Product.objects.all().filter(is_available=True)
    banner_images = ProductBannerImage.objects.all()
    context = {"banner_images": banner_images, "products": products, 
               "categories": Category.objects.all(),}
    return render(request, "home.html", context)


def contact(request):
    """
    Render the contact page.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML template for the contact page.
    """
    return render(request, "contact.html")


def about(request):
    """
    Render the about page.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML template for the about page.
    """
    return render(request, "about.html")


from django.db.models import F

def store(request, category_slug=None):
    categories = None
    variations = None
    brand_filter = request.GET.get("brand")
    frame_size_filters = request.GET.getlist("frame-size")
    min_price = request.GET.get("min-price")
    max_price = request.GET.get("max-price")
    category_filter = request.GET.get("category")  # New category filter

    if category_slug:
        categories = get_object_or_404(Category, slug=category_slug)
        variations = ProductVariation.objects.filter(product__category=categories)
    else:
        variations = ProductVariation.objects.all()

    if brand_filter and brand_filter != "All":
        variations = variations.filter(product__brand=brand_filter)

    if frame_size_filters:
        variations = variations.filter(frame_size__in=frame_size_filters)

    if min_price and max_price:
        variations = variations.filter(
            product__price__range=(min_price, max_price)
        )

    if category_filter:  # Apply category filter if selected
        variations = variations.filter(product__category__category_name=category_filter)

    product_ids = variations.values_list("product__id", flat=True).distinct()
    products = Product.objects.filter(id__in=product_ids)

    paginator = Paginator(products, 3)
    page = request.GET.get("page")
    paged_products = paginator.get_page(page)
    product_count = len(product_ids)

    for product in paged_products:
        discount_percentage = (
            (product.rprice - product.price) / product.rprice * 100
        )

    context = {
        "products": paged_products,
        "product_count": product_count,
        "categories": Category.objects.all(),  # Provide categories for template rendering
    }
    return render(request, "store.html", context)


def search(request):
    query = request.GET.get("keyword")

    categories = None
    products = Product.objects.filter(is_available=True)

    if query:
        # Filter the products based on the search keyword
        products = products.filter(
            models.Q(brand__icontains=query) | models.Q(model__icontains=query)
        )

    paginator = Paginator(products, 3)
    page = request.GET.get("page")
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {
        "products": paged_products,
        "product_count": product_count,
    }
    return render(request, "store.html", context)


def product_details(request, category_slug, product_slug):
    try:
        single_product = get_object_or_404(
            Product, category__slug=category_slug, slug=product_slug
        )
        in_cart = CartItem.objects.filter(
            cart__cart_id=_cart_id(request), product=single_product
        ).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(
                user=request.user, product_id=single_product.id
            ).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

    # Get color and size variations separately
    colors = single_product.productvariation_set.filter(color__isnull=False)
    all_sizes = single_product.productvariation_set.filter(
        frame_size__isnull=False
    )

    # Filter out unique frame sizes using a set
    unique_sizes_set = set()
    unique_sizes = []
    for size in all_sizes:
        if size.frame_size not in unique_sizes_set:
            unique_sizes_set.add(size.frame_size)
            unique_sizes.append(size)

    # Get the reviews
    product_images = ProductImage.objects.filter(product=single_product)
    logging.warning(product_images)

    context = {
        "product_images": product_images,
        "single_product": single_product,
        "in_cart": in_cart,
        "orderproduct": orderproduct,
        "colors": colors,
        "sizes": unique_sizes,  # Use the filtered unique sizes here
    }
    return render(request, "product_details.html", context)


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            phone_number = form.cleaned_data["phone_number"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            username = email.split("@")[0]
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                phone_number=phone_number,
                email=email,
                username=username,
                password=password,
            )
            user.is_active = True
            user.save()
            messages.success(
                request,
                "Thank you for registering with us. now you can login to your account!",
            )
            return redirect("login")
    else:
        form = RegistrationForm()
    context = {
        "form": form,
    }
    return render(request, "user/register.html", context)


import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import authenticate, login
from twilio.rest import Client


def custom_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            request.session["email"] = email
            request.session["password"] = password
            phone_number = user.phone_number
            verification = send_otp(
                phone_number
            )  # Assuming send_otp function is defined
            print(".................", verification)

            # Save verification details in session
            request.session["otp_verification_sid"] = verification.sid
            request.session["verified_number"] = phone_number

            messages.success(
                request, "OTP is sent to your registered mobile number"
            )
            return redirect("/login/otp/")
        else:
            messages.error(request, "Username or password is wrong")

    return render(request, "user/login.html")


def verify_otp(request):
    if request.method == "POST":
        user_otp = request.POST.get("otp")
        email = request.session["email"]
        password = request.session["password"]

        # Get Twilio verification details from session
        verification_sid = request.session.get("otp_verification_sid")
        verified_number = request.session.get("verified_number")

        # Verify the OTP code with Twilio
        client = Client(
            settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN
        )
        verification_check = client.verify.v2.services(
            settings.TWILIO_VERIFY_SID
        ).verification_checks.create(to=verified_number, code=user_otp)

        logging.warning(verification_check.status)

        if verification_check.status == "approved":
            # OTP verification successful, proceed with login
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                # Cleanup session after successful login
                del request.session["email"]
                del request.session["password"]
                del request.session["otp_verification_sid"]
                del request.session["verified_number"]

                messages.success(request, "Login successful")
                return redirect("/")
        else:
            messages.error(request, "Wrong OTP")

    return render(request, "user/verify_otp.html")


def custom_logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out.")
    return redirect("login")


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset password email
            current_site = get_current_site(request)
            mail_subject = "Reset Your Password"
            message = render_to_string(
                "user/reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request,
                "Password reset email has been sent to your email address.",
            )
            return redirect("login")
        else:
            messages.error(request, "Account does not exist!")
            return redirect("forgotPassword")
    return render(request, "user/forgotPassword.html")


def resetpassword_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session["uid"] = uid
        messages.success(request, "Please reset your password")
        return redirect("resetPassword")
    else:
        messages.error(request, "This link has been expired!")
        return redirect("login")


@login_required
def resetPassword(request):
    if request.method == "POST":
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password == confirm_password:
            user = request.user
            user.set_password(password)
            user.save()
            messages.success(request, "Password reset successful")
            return redirect("login")
        else:
            messages.error(request, "Password do not match!")
            return redirect("resetPassword")
    else:
        return render(request, "user/resetPassword.html")


@login_required
def user_profile(request):
    user = request.user

    context = {"user": user}
    return render(request, "user/user_profile.html", context)


@login_required
def edit_profile(request):
    user = request.user

    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user_profile")

    else:
        form = UserProfileForm(instance=user)

    context = {"form": form}
    return render(request, "user/edit_profile.html", context)


@login_required
def order_details(request, order_number):
    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
            "order": order,
            "ordered_products": ordered_products,
            "order_number": order.order_number,
            "subtotal": subtotal,
        }
        return render(request, "user/order_details.html", context)
    except Order.DoesNotExist:
        return redirect("store")


@login_required
def dashboard(request):
    try:
        if request.user.is_authenticated:
            orders = Order.objects.filter(
                user=request.user, is_ordered=True
            ).order_by("-id")

            context = {
                "orders": orders,
            }
            return render(request, "user/dashboard.html", context)
        else:
            return redirect("store")
    except Order.DoesNotExist:
        return redirect("store")


@login_required
def received_orders(request):
    try:
        if request.user.is_authenticated:
            orders = Order.objects.filter(
                user=request.user, is_ordered=True, status="Completed"
            ).order_by("-id")

            context = {
                "orders": orders,
            }
            return render(request, "user/received_orders.html", context)
        else:
            return redirect("store")
    except Order.DoesNotExist:
        return redirect("store")


@login_required
def returned_orders(request):
    try:
        if request.user.is_authenticated:
            orders = Order.objects.filter(
                user=request.user, is_ordered=True, status="Completed"
            ).order_by("-id")

            context = {
                "orders": orders,
            }
            return render(request, "user/returned_orders.html", context)
        else:
            return redirect("store")
    except Order.DoesNotExist:
        return redirect("store")


# Addresses


@login_required
def view_address(request):
    addresses = Address.objects.filter(customer=request.user)
    return render(request, "user/addresses.html", {"addresses": addresses})


@login_required
def add_address(request):
    if request.method == "POST":
        address_form = UserAddressForm(data=request.POST)
        if address_form.is_valid():
            address_form = address_form.save(commit=False)
            address_form.customer = request.user
            address_form.save()
            return HttpResponseRedirect(reverse("addresses"))
    else:
        address_form = UserAddressForm()
    return render(request, "user/edit_addresses.html", {"form": address_form})


def add_address_checkout(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        if request.method == "POST":
            address_form = UserAddressForm(data=request.POST)
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.customer = request.user
                address.save()
                return HttpResponseRedirect(reverse("checkout"))
        else:
            address_form = UserAddressForm()

    return render(request, "user/edit_addresses.html", {"form": address_form})


@login_required
def edit_address(request, id):
    if request.method == "POST":
        address = Address.objects.get(pk=id, customer=request.user)
        address_form = UserAddressForm(instance=address, data=request.POST)
        if address_form.is_valid():
            address_form.save()
            return HttpResponseRedirect(reverse("addresses"))
    else:
        address = Address.objects.get(pk=id, customer=request.user)
        address_form = UserAddressForm(instance=address)
    return render(request, "user/edit_addresses.html", {"form": address_form})


@login_required
def edit_address_checkout(request, id):
    if request.method == "POST":
        address = Address.objects.get(pk=id, customer=request.user)
        address_form = UserAddressForm(instance=address, data=request.POST)
        if address_form.is_valid():
            address_form.save()
            return HttpResponseRedirect(reverse("checkout"))
    else:
        address = Address.objects.get(pk=id, customer=request.user)
        address_form = UserAddressForm(instance=address)
    return render(request, "user/edit_addresses.html", {"form": address_form})


@login_required
def delete_address(request, id):
    address = Address.objects.filter(pk=id, customer=request.user).delete()
    return redirect("addresses")


@login_required
def delete_address_checkout(request, id):
    address = Address.objects.filter(pk=id, customer=request.user).delete()
    return redirect("checkout")


@login_required
def set_default_checkout(request, id):
    Address.objects.filter(customer=request.user, default=True).update(
        default=False
    )
    Address.objects.filter(pk=id, customer=request.user).update(default=True)
    return redirect("checkout")


@login_required
def set_default(request, id):
    Address.objects.filter(customer=request.user, default=True).update(
        default=False
    )
    Address.objects.filter(pk=id, customer=request.user).update(default=True)
    return redirect("addresses")


###########################################################################


@login_required(login_url="admin_login")
def order_management(request):
    try:
        orders = Order.objects.filter(is_ordered=True).order_by("-id")

        context = {
            "orders": orders,
        }
        return render(request, "admin/order_management.html", context)
    except Order.DoesNotExist:
        return redirect("admin_dashboard")


@login_required(login_url="admin_login")
def update_order_status(request, order_number):
    order = get_object_or_404(
        Order, order_number=order_number, is_ordered=True
    )

    if request.method == "POST":
        status = request.POST.get("status")
        if status in [choice[0] for choice in Order.STATUS]:
            order.status = status
            order.save()
            messages.success(request, "Order status updated successfully.")
        else:
            messages.error(request, "Invalid status value.")
    orders = Order.objects.all().filter(is_ordered=True).order_by("-id")
    return render(request, "admin/order_management.html", {"orders": orders})


@login_required(login_url="admin_login")
def admin_dashboard(request):
    today = datetime.now()
    start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    daily_sales_amount = Order.objects.filter(
        created_at__range=(start_date, end_date), is_ordered=True
    ).aggregate(total_sales=Sum("order_total"))["total_sales"]

    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)
    weekly_sales_amount = Order.objects.filter(
        created_at__range=(start_date, end_date), is_ordered=True
    ).aggregate(total_sales=Sum("order_total"))["total_sales"]

    start_date = today.replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    )
    end_date = (start_date + timedelta(days=32)).replace(
        day=1, hour=0, minute=0, second=0, microsecond=0
    ) - timedelta(seconds=1)
    monthly_sales_amount = Order.objects.filter(
        created_at__range=(start_date, end_date), is_ordered=True
    ).aggregate(total_sales=Sum("order_total"))["total_sales"]

    start_date = today.replace(
        month=1, day=1, hour=0, minute=0, second=0, microsecond=0
    )
    end_date = today.replace(
        month=12, day=31, hour=23, minute=59, second=59, microsecond=999999
    )
    yearly_sales_amount = Order.objects.filter(
        created_at__range=(start_date, end_date), is_ordered=True
    ).aggregate(total_sales=Sum("order_total"))["total_sales"]

    recent_transactions = Order.objects.filter(is_ordered=True).order_by(
        "-created_at"
    )[:5]

    top_three_products = Product.objects.annotate(
        order_count=Count("orderproduct")
    ).order_by("-order_count")[:3]

    orders = Order.objects.all().order_by("-id")
    context = {
        "daily_sales_amount": daily_sales_amount,
        "weekly_sales_amount": weekly_sales_amount,
        "monthly_sales_amount": monthly_sales_amount,
        "yearly_sales_amount": yearly_sales_amount,
        "recent_transactions": recent_transactions,
        "top_three_products": top_three_products,
        "orders": orders,
    }
    return render(request, "admin/dashboard.html", context)


import csv
from django.http import HttpResponse


def download_order_data(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="order_data.csv"'

    orders = Order.objects.all()

    writer = csv.writer(response)
    writer.writerow(
        [
            "Order Number",
            "Name",
            "Phone",
            "Email",
            "City",
            "Amount",
            "Tax",
            "Status",
            "Is Ordered",
            "Created At",
        ]
    )

    for order in orders:
        writer.writerow(
            [
                order.order_number,
                f"{order.first_name} {order.last_name}",
                order.phone,
                order.email,
                order.city,
                order.order_total,
                order.tax,
                order.status,
                order.is_ordered,
                order.created_at,
            ]
        )

    return response


def admin_login(request):
    """
    Authenticate and log in the user.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML template for login or a redirect response on successful login.
    """
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(email=email, password=password)
        if user.is_staff:
            login(request, user)
            messages.success(
                request, f"Hello {user.username}! You have been logged in"
            )
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Invalid credentials ")

    products = Product.objects.all()
    banner_images = ProductBannerImage.objects.all()

    return render(
        request=request,
        template_name="admin/admin_login.html",
        context={"banner_images": banner_images, "products": products},
    )


@login_required(login_url="admin_login")
def admin_logout(request):
    """
    Log out the currently authenticated user.

    Args:
        request: The HTTP request object.

    Returns:
        A redirect response after logging out the user.
    """
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("admin_login")


@login_required(login_url="admin_login")
def admin_home(request):
    """
    Render the admin home page.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML template for the admin home page.
    """
    return render(request, "admin/admin_home.html")


@login_required(login_url="admin_login")
def admin_user_view(request):
    """
    View and manage user details for admin.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML template for admin user view.
    """
    user_details = Account.objects.exclude(is_staff=True)
    context = {"user_details": user_details}
    return render(request, "admin/admin_user_view.html", context)


@login_required(login_url="admin_login")
def admin_user_block(request):
    """
    Block or unblock a user for admin.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML template for admin user view.
    """
    id = request.GET.get("id")
    user_details = Account.objects.get(id=id)
    if user_details.is_active:
        user_details.is_active = False
        user_details.save()
    else:
        user_details.is_active = True
        user_details.save()
    user_details = Account.objects.exclude(is_staff=True)
    context = {"user_details": user_details}
    return render(request, "admin/admin_user_view.html", context)


@login_required(login_url="admin_login")
def admin_product_view(request):
    """
    View and manage product details for admin.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML template for admin product view.
    """
    prd_details = Product.objects.all().order_by("-id")
    cat_details = Category.objects.all()
    context = {
        "prd_details": prd_details,
        "cat_details": cat_details,
    }
    return render(request, "admin/admin_product_view.html", context)


@login_required(login_url="admin_login")
def admin_product_add(request):
    """
    Add a new product in the admin panel.

    Args:
        request: The HTTP request object.

    Returns:
        If the form is valid, redirects to the admin product view page.
        Otherwise, renders the admin product add page with the form.
    """
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the Product instance
            product = form.save(commit=False)
            product.rprice = product.price
            product.save()

            # Create the ProductImage instances
            images = request.FILES.getlist("image")
            product.image = images[0]
            product.save()

            for image in images:
                ProductImage.objects.create(product=product, image=image)

            messages.success(request, "Product added successfully")
            return redirect("admin_product_view")
    else:
        form = ProductForm()

    return render(request, "admin/admin_product_add.html", {"form": form})


@login_required(login_url="admin_login")
def admin_category_view(request):
    """
    View and manage categories in the admin panel.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML template for admin category view.
    """
    cat_details = Category.objects.all()
    context = {"cat_details": cat_details}
    return render(request, "admin/admin_category_view.html", context)


@login_required(login_url="admin_login")
def admin_category_add(request):
    """
    Add a new category in the admin panel.

    Args:
        request: The HTTP request object.

    Returns:
        If the category is successfully created, redirects to the admin category view page.
        Otherwise, renders the admin category add page.
    """
    if request.method == "POST":
        cat_name = request.POST["name"]
        Category.objects.create(category_name=cat_name)
        messages.success(request, f"Category added successfully")
        cat_details = Category.objects.all()
        context = {"cat_details": cat_details}
        return render(request, "admin/admin_category_view.html", context)
    return render(request, "admin/admin_category_add.html")


@login_required(login_url="admin_login")
def admin_category_delete(request):
    """
    Delete a category in the admin panel.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML template for admin category view.
    """
    uid = request.GET.get("uid")
    cat_details = Category.objects.get(uid=uid)
    cat_details.delete()
    messages.error(request, "Category deleted successfully")
    cat_details = Category.objects.all()
    context = {"cat_details": cat_details}
    return render(request, "admin/admin_category_view.html", context)


@login_required(login_url="admin_login")
def admin_category_edit(request):
    """
    Edit a category in the admin panel.

    Args:
        request: The HTTP request object.

    Returns:
        If the category is successfully edited, redirects to the admin category view page.
        Otherwise, renders the admin category edit page.
    """
    if request.method == "POST":
        cat_name = request.POST["name"]
        c_uid = request.POST["uid"]
        cat = Category.objects.get(uid=c_uid)
        cat.category_name = cat_name
        cat.save()
        messages.warning(request, f"Category edited successfully")
        cat = Category.objects.all()
        context = {"cat_details": cat, "uid": c_uid}
        return render(request, "admin/admin_category_view.html", context)
    c_uid = request.GET["uid"]
    cat = Category.objects.get(uid=c_uid)
    context = {"cat": cat, "uid": c_uid}
    return render(request, "admin/admin_category_edit.html", context)


@login_required(login_url="admin_login")
def admin_product_delete(request):
    """
    Delete a product in the admin panel.

    Args:
        request: The HTTP request object.

    Returns:
        A rendered HTML template for admin product view.
    """
    P_id = request.GET.get("id")
    prd_details = Product.objects.get(id=P_id)
    prd_details.delete()
    prd_details = Product.objects.all()
    cat_details = Category.objects.all()
    messages.error(request, "product deleted successfully")
    context = {
        "prd_details": prd_details,
        "cat_details": cat_details,
    }
    return render(request, "admin/admin_product_view.html", context)


@login_required(login_url="admin_login")
def admin_product_update(request, product_id):
    """
    Update a product in the admin panel.

    Args:
        request: The HTTP request object.
        product_id: The ID of the product to be updated.

    Returns:
        If the form is valid, redirects to the admin product view page.
        Otherwise, renders the admin product update page with the form.
    """
    product = Product.objects.get(id=product_id)

    if request.method == "POST":
        form = ProductUpdateForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            product.rprice = product.price
            product.save()

            images = request.FILES.getlist("image")
            for image in images:
                ProductImage.objects.create(product=product, image=image)

            messages.warning(request, "Product edited successfully")
            return redirect("admin_product_view")
    else:
        form = ProductUpdateForm(instance=product)

    return render(
        request,
        "admin/admin_product_update.html",
        {"form": form, "product": product},
    )


@login_required(login_url="admin_login")
def add_product_variation(request, product_id):
    product = Product.objects.get(pk=product_id)

    if request.method == "POST":
        form = ProductVariationForm(request.POST)
        if form.is_valid():
            frame_size = form.cleaned_data["frame_size"]
            color = form.cleaned_data["color"]
            stock = form.cleaned_data["stock"]

            # Check if a variation with the same frame_size and color exists for the product
            existing_variation = ProductVariation.objects.filter(
                product=product, frame_size=frame_size, color=color
            ).first()

            if existing_variation:
                # If a variation already exists, update its stock
                existing_variation.stock += stock
                existing_variation.save()
            else:
                # If no variation exists, create a new ProductVariation instance
                ProductVariation.objects.create(
                    product=product,
                    frame_size=frame_size,
                    color=color,
                    stock=stock,
                )

            return redirect("product_variations", product_id=product_id)

    else:
        form = ProductVariationForm()

    context = {
        "product": product,
        "form": form,
    }

    return render(request, "admin/add_product_variation.html", context)


@login_required(login_url="admin_login")
def edit_product_variation(request, variation_id):
    variation = get_object_or_404(ProductVariation, pk=variation_id)

    if request.method == "POST":
        form = ProductVariationForm(request.POST, instance=variation)
        if form.is_valid():
            stock = form.cleaned_data["stock"]

            # Assign the new stock value to the existing ProductVariation
            variation.stock = stock
            variation.save()

            return redirect(
                "product_variations", product_id=variation.product.id
            )
    else:
        form = ProductVariationForm(instance=variation)

    context = {
        "variation": variation,
        "form": form,
    }

    return render(request, "admin/edit_product_variation.html", context)


@login_required(login_url="admin_login")
def delete_product_variation(request, variation_id):
    variation = get_object_or_404(ProductVariation, pk=variation_id)
    variation.delete()
    return redirect("product_variations", product_id=variation.product.id)


@login_required(login_url="admin_login")
def product_variations_view(request, product_id):
    logging.warning("...........................")
    # Retrieve the specific Product instance or return a 404 if not found
    product = get_object_or_404(Product, pk=product_id)

    # Retrieve all ProductVariation instances for the specific product
    product_variations = ProductVariation.objects.filter(product=product)

    return render(
        request,
        "admin/product_variations.html",
        {"product_variations": product_variations, "product": product},
    )
