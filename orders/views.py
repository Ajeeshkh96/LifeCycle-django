from __future__ import annotations

import datetime
import json
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from paypal.standard.forms import PayPalPaymentsForm

from .forms import CouponForm
from .forms import OrderForm
from .models import Coupon
from .models import Order
from .models import OrderProduct
from .models import Payment
from .models import ReturnItem
from .models import ReturnRequest
from .models import Wallet
from .models import WalletTransaction
from carts.models import CartItem
from users.models import Address
from users.models import Product
from users.models import ProductVariation

# Create your views here.


def payments(request):
    # Check if the request is a POST request
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method."}, status=400)

    # Load the request body as JSON
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON data in the request body."}, status=400
        )

    # Ensure required fields are present in the request
    required_fields = ["orderID", "transID", "payment_method", "status"]
    for field in required_fields:
        if field not in body:
            return JsonResponse(
                {"error": f"Missing '{field}' in the request body."},
                status=400,
            )

    try:
        order = Order.objects.get(
            user=request.user, is_ordered=False, order_number=body["orderID"]
        )
    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found."}, status=404)

    # Store transaction details inside Payment model
    payment = Payment(
        user=request.user,
        payment_id=body["transID"],
        payment_method=body["payment_method"],
        amount_paid=order.order_total,
        status=body["status"],
    )
    payment.save()
    # Mark the order as paid and save it
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct(
            order=order,
            payment=payment,
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True,
            variation=item.variation,
        )
        orderproduct.save()

        # Reduce the quantity of the sold products
        product_variation = item.variation
        product_variation.stock -= item.quantity
        product_variation.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    mail_subject = "Thank you for your order!"
    message = render_to_string(
        "orders/order_complete.html",
        {
            "user": request.user,
            "order": order,
        },
    )
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    data = {
        "order_number": order.order_number,
        "transID": payment.payment_id,
    }
    return JsonResponse(data)


import uuid


def generate_unique_payment_id(user_id):
    current_datetime = timezone.now()
    random_string = str(uuid.uuid4()).replace("-", "")
    payment_id = f'{current_datetime.strftime("%Y%m%d%H%M%S")}_{user_id}_{random_string}'
    return payment_id


def payment_through_wallet(request, order_number):
    try:
        order = Order.objects.get(
            user=request.user, is_ordered=False, order_number=order_number
        )

        # wallet = Wallet.objects.get(user=request.user)
        # wallet.balance -= Decimal(
        #     order.order_total
        # )  # Deduct the order total from the wallet balance
        # wallet.save()

        try:
            wallet = Wallet.objects.get(user=request.user)
            if wallet.balance < Decimal(order.order_total):
                return JsonResponse({"error": "Insufficient wallet balance."}, status=400)

            wallet.balance -= Decimal(order.order_total)
            wallet.save()

        except Wallet.DoesNotExist:
            # Create a wallet for the user
            wallet = Wallet.objects.create(user=request.user, balance=Decimal(0))
            return JsonResponse({"message": "Wallet created. Add funds to place an order."})

    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found."}, status=404)

    payment_id = generate_unique_payment_id(request.user.id)
    # Store transaction details inside Payment model
    payment = Payment(
        user=request.user,
        payment_id=payment_id,
        payment_method="wallet",
        amount_paid=order.order_total,
        status="COMPLETED",
    )
    payment.save()
    # Mark the order as paid and save it
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct(
            order=order,
            payment=payment,
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True,
            variation=item.variation,
        )
        orderproduct.save()

        # Reduce the quantity of the sold products
        product_variation = item.variation
        product_variation.stock -= item.quantity
        product_variation.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    mail_subject = "Thank you for your order!"
    message = render_to_string(
        "orders/order_complete.html",
        {
            "user": request.user,
            "order": order,
        },
    )
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=payment_id)

        context = {
            "order": order,
            "ordered_products": ordered_products,
            "order_number": order.order_number,
            "transID": payment_id,
            "payment": payment,
            "subtotal": subtotal,
        }
        return render(request, "orders/order_complete.html", context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect("home")
    

def cash_on_delivery(request, order_number):
    try:
        order = Order.objects.get(
            user=request.user, is_ordered=False, order_number=order_number
        )

    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found."}, status=404)

    payment_id = generate_unique_payment_id(request.user.id)
    # Store transaction details inside Payment model
    payment = Payment(
        user=request.user,
        payment_id=payment_id,
        payment_method="cash_on_delivery",
        amount_paid=0,  # No payment needed for COD
        status="PENDING",  # COD payments are pending until delivery
    )
    payment.save()
    # Mark the order as paid and save it
    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product table
    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct(
            order=order,
            payment=payment,
            user=request.user,
            product=item.product,
            quantity=item.quantity,
            product_price=item.product.price,
            ordered=True,
            variation=item.variation,
        )
        orderproduct.save()

        # Reduce the quantity of the sold products
        product_variation = item.variation
        product_variation.stock -= item.quantity
        product_variation.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    mail_subject = "Thank you for your order!"
    message = render_to_string(
        "orders/order_complete.html",
        {
            "user": request.user,
            "order": order,
        },
    )
    to_email = request.user.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

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
            "transID": payment_id,
            "payment": payment,
            "subtotal": subtotal,
        }
        return render(request, "orders/order_complete.html", context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect("home")



def redeem_coupon_payment(request, order_number):
    if request.method == "POST":
        current_user = request.user
        order = Order.objects.get(
            user=current_user, is_ordered=False, order_number=order_number
        )

        code = request.POST.get("code")

        try:
            coupon = Coupon.objects.get(
                code=code,
                redeemed_by__isnull=True,
                active=True,
                valid_to__gte=timezone.now(),
            )
            coupon.redeemed_by = request.user
            coupon.save()

            discount_amount = float(coupon.discount_amount)
            order.order_total -= discount_amount
            order.save()
            print("order.total==", order.order_total)
            return JsonResponse(
                {
                    "grand_total": str(order.order_total),
                    "discount_amount": str(discount_amount),
                }
            )

        except Coupon.DoesNotExist:
            pass

    return render(request, "user/coupon_redeem.html")


def place_order(
    request,
    total=0,
    quantity=0,
):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("store")

    if request.method == "POST":
        grand_total = 0
        total = Decimal(0)
        tax = 0
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
        tax = Decimal(2) * total / 100
        grand_total = total + tax

        form = OrderForm(request.POST)
        if form.is_valid():
            print("...............next form valid")
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data["first_name"]
            data.last_name = form.cleaned_data["last_name"]
            data.phone = form.cleaned_data["phone"]
            data.email = form.cleaned_data["email"]
            data.address_line_1 = form.cleaned_data["address_line_1"]
            data.address_line_2 = form.cleaned_data["address_line_2"]
            data.country = form.cleaned_data["country"]
            data.state = form.cleaned_data["state"]
            data.city = form.cleaned_data["city"]
            data.pin_code = form.cleaned_data["pin_code"]
            data.order_note = form.cleaned_data["order_note"]
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get("REMOTE_ADDR")
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime("%Y"))
            dt = int(datetime.date.today().strftime("%d"))
            mt = int(datetime.date.today().strftime("%m"))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")  # 20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(
                user=current_user, is_ordered=False, order_number=order_number
            )
            print(".............................next2222222222222222222222")
            print("...grand total", grand_total)
            context = {
                "order": order,
                "cart_items": cart_items,
                "total": total,
                "tax": tax,
                "grand_total": grand_total,
            }
            return render(request, "orders/payments.html", context)
    else:
        return redirect("checkout")


def order_complete(request):
    order_number = request.GET.get("order_number")
    transID = request.GET.get("payment_id")

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=transID)

        context = {
            "order": order,
            "ordered_products": ordered_products,
            "order_number": order.order_number,
            "transID": payment.payment_id,
            "payment": payment,
            "subtotal": subtotal,
        }
        return render(request, "orders/order_complete.html", context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect("home")


def cancel_order(request, order_number):
    try:
        order = Order.objects.get(
            order_number=order_number, user=request.user, is_ordered=True
        )
        # Check if the order can be cancelled based on its current status
        if not order.can_be_cancelled():
            return HttpResponse("Cannot cancel this order.")
        
        # Check if the payment method was not cash on delivery
        if order.payment.payment_method != "cash_on_delivery":
            # Calculate the total payment amount
            payment_amount = Decimal(order.order_total)

            try:
                wallet = Wallet.objects.get(user=request.user)
                wallet.balance += payment_amount
                wallet.save()

            except Wallet.DoesNotExist:
                # Create a wallet for the user
                wallet = Wallet.objects.create(user=request.user, balance=payment_amount)

            # Display a success message about the wallet credit
            wallet_credit_msg = f"Order cancelled. Amount credited to your wallet: {order.order_total}"
            messages.success(request, wallet_credit_msg)

        # Mark the order as canceled and update product stock
        ordered_products = OrderProduct.objects.filter(order=order)
        for variation in ordered_products:
            variation.variation.stock += variation.quantity
            variation.variation.save()
        order.status = "Cancelled"
        order.save()

        # Send email notification to the customer
        mail_subject = "Order Cancellation"
        message = render_to_string(
            "orders/order_recieved_email.html",
            {
                "user": request.user,
                "order": order,
            },
        )
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()

        return redirect("dashboard")

    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect("home")


def coupon_view(request):
    coupons = Coupon.objects.filter(active=True, valid_to__gte=timezone.now())
    return render(request, "user/coupon_view.html", {"coupons": coupons})


from django.shortcuts import redirect


def return_request_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return_request = None

    try:
        return_request = ReturnRequest.objects.get(order=order)
    except ReturnRequest.DoesNotExist:
        pass

    if request.method == "POST":
        return_items = request.POST.getlist("return_items")
        reason = request.POST.get("reason")

        if return_items:
            # Check if a return request already exists for this order
            return_request, created = ReturnRequest.objects.get_or_create(
                order=order, defaults={"reason": reason}
            )

            if not created:
                messages.info(
                    request,
                    "A return request already exists for this order. Adding items to the existing request.",
                )

            order_products = OrderProduct.objects.filter(id__in=return_items)
            for order_product in order_products:
                return_item, created = ReturnItem.objects.get_or_create(
                    return_request=return_request
                )
                return_item.returned_items.add(order_product)

            orders = Order.objects.filter(
                user=request.user, is_ordered=True, status="Completed"
            ).order_by("-id")

            context = {
                "orders": orders,
            }
            messages.success(request, "Return requested successfully")
            return render(request, "user/received_orders.html", context)
        else:
            orders = Order.objects.filter(
                user=request.user, is_ordered=True, status="Completed"
            )

            context = {
                "orders": orders,
            }
            messages.error(request, "Please select at least one item")
            return render(
                request, "user/return_request.html", {"order": order}
            )

    return render(
        request,
        "user/return_request.html",
        {"order": order, "return_request": return_request},
    )


############################### ADMIN ###############################################################


@login_required(login_url="admin_login")
def add_coupon(request):
    if request.method == "POST":
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("view_coupons")
    else:
        form = CouponForm()

    return render(request, "admin/add_coupon.html", {"form": form})


@login_required(login_url="admin_login")
def view_coupons(request):
    coupons = Coupon.objects.filter(active=True, valid_to__gte=timezone.now())
    return render(request, "admin/view_coupons.html", {"coupons": coupons})


@login_required
def add_wallet(request):
    if request.method == "POST":
        if "money" in request.POST:
            return redirect("view_wallet")

        elif "coupon" in request.POST:
            return redirect("view_wallet")

        user = request.user

        if Wallet.objects.filter(user=user).exists():
            return redirect("view_wallet")

        Wallet.objects.create(user=user)
        messages.success(request, "Wallet created successfully")
        return redirect("view_wallet")
    else:
        user = request.user
        wallet = None
        try:
            wallet = Wallet.objects.get(user=user)
        except Wallet.DoesNotExist:
            pass
        return render(request, "user/wallet_add.html", {"wallet": wallet})


@login_required
def view_wallet(request):
    user = request.user
    wallet = Wallet.objects.get(user=user)

    context = {
        "wallet": wallet,
    }
    return render(request, "user/wallet_view.html", context)


def update_wallet(request):
    user = request.user
    wallet = Wallet.objects.get(user=user)

    if request.method == "POST":
        print("..........111111111")
        amount = Decimal(request.POST.get("amount", "0"))
        wallet.balance += amount
        wallet.save()
        return render(request, "user/wallet_update.html")

    return render(request, "user/wallet_update.html")


def redeem_coupon(request):
    user = request.user
    try:
        if Wallet.objects.filter(user=user).exists():
            wallet = Wallet.objects.get(user=user)
        else:
            wallet = Wallet.objects.create(user=user)
            messages.success(request, "Wallet created Successfully")
    except:
        pass

    if request.method == "POST":
        code = request.POST.get("code")
        try:
            coupon = Coupon.objects.get(
                code=code,
                redeemed_by__isnull=True,
                active=True,
                valid_to__gte=timezone.now(),
            )
            coupon.redeemed_by = request.user
            coupon.save()

            wallet.balance += coupon.discount_amount
            wallet.save()

            messages.success(
                request,
                f"Coupon redeemed Successfully $ {coupon.discount_amount} added to your wallet",
            )

        except Coupon.DoesNotExist:
            messages.error(
                request,
                "Coupon Already Redeemed",
            )

    return render(request, "user/coupon_redeem.html")


from django.db.models import Q


@login_required(login_url="admin_login")
def view_returns(request):
    try:
        returned_orders = (
            Order.objects.filter(
                Q(orderproduct__returnitem__status="Processing")
                | Q(orderproduct__returnitem__status="Completed")
                | Q(orderproduct__returnitem__status="Rejected")
            )
            .distinct()
            .order_by("-id")
        )
        context = {
            "orders": returned_orders,
        }
        return render(request, "admin/view_returns.html", context)
    except Order.DoesNotExist:
        return redirect("admin_dashboard")


def view_return_items(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    return_request = None

    try:
        return_request = ReturnRequest.objects.get(order=order)
    except ReturnRequest.DoesNotExist:
        pass

    context = {
        "order": order,
        "return_request": return_request,
    }
    return render(request, "admin/view_return_items.html", context)


@login_required(login_url="admin_login")
def update_return_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    try:
        return_request = ReturnRequest.objects.get(order=order)
        return_item = ReturnItem.objects.get(return_request=return_request)
    except (ReturnRequest.DoesNotExist, ReturnItem.DoesNotExist):
        return redirect("admin:view_returns")

    if request.method == "POST":
        status = request.POST.get("status")

        if status == "Accepted":
            if return_request.status == "Accepted":
                messages.error(request, "Return status already updated")
            else:
                return_request.status = "Accepted"
                return_request.save()
                return_item.status = "Completed"
                return_item.save()

                if not WalletTransaction.objects.filter(
                    wallet__user=order.user, order=order
                ).exists():
                    try:
                        wallet = Wallet.objects.get(user=order.user)
                    except Wallet.DoesNotExist:
                        wallet = Wallet.objects.create(user=order.user)

                    wallet.balance += Decimal(order.order_total)
                    wallet.save()

                    WalletTransaction.objects.create(
                        wallet=wallet,
                        order=order,
                        amount=Decimal(order.order_total),
                    )

                    messages.success(
                        request, "Return Accepted. Wallet amount updated."
                    )
                else:
                    messages.error(
                        request,
                        "Return status updated. Wallet amount already updated",
                    )

        elif status == "Rejected":
            return_request.status = "Rejected"
            return_request.save()
            return_item.status = "Rejected"
            return_item.save()
            messages.error(request, "Return Rejected.")
        else:
            messages.error(request, "Invalid status value.")

    orders = Order.objects.filter(
        is_ordered=True,
        return_requests__status__in=[
            "Pending",
            "Accepted",
            "Rejected",
            "Completed",
        ],
    ).order_by("-id")
    return render(request, "admin/view_returns.html", {"orders": orders})
