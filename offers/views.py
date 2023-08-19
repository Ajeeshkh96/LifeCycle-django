from __future__ import annotations

from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView

from .forms import OfferForm
from .forms import ProductBannerImageForm
from .models import Offer
from users.models import ProductBannerImage


class BannerImageListView(ListView):
    model = ProductBannerImage
    template_name = "admin/view_banner_image_list.html"
    context_object_name = "images"


class BannerImageCreateView(CreateView):
    model = ProductBannerImage
    form_class = ProductBannerImageForm
    template_name = "admin/add_banner_image.html"
    success_url = reverse_lazy("product_banner_list")


class BannerImageUpdateView(UpdateView):
    model = ProductBannerImage
    form_class = ProductBannerImageForm
    template_name = "admin/edit_banner_image.html"
    context_object_name = "image"
    success_url = reverse_lazy("product_banner_list")


class BannerImageDeleteView(DeleteView):
    model = ProductBannerImage
    template_name = "admin/banner_confirm_delete.html"
    context_object_name = "image"
    success_url = reverse_lazy("product_banner_list")

    def delete(self, request, *args, **kwargs):
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect(self.success_url)


class OfferCreateView(CreateView):
    model = Offer
    form_class = OfferForm
    template_name = "admin/offer_form.html"
    success_url = reverse_lazy(
        "offer_list"
    )  # Redirect after successful creation

    def form_valid(self, form):
        response = super().form_valid(form)

        offer = form.instance
        applicable_products = offer.applicable_products.all()
        for product in applicable_products:
            discounted_price = product.price * (
                1 - offer.discount_percentage / 100
            )
            product.price = discounted_price
            product.save()

        return response


class OfferListView(ListView):
    model = Offer
    template_name = "admin/offer_list.html"
    context_object_name = "offers"


class OfferUpdateView(UpdateView):
    model = Offer
    form_class = OfferForm
    template_name = "admin/offer_form.html"
    success_url = reverse_lazy(
        "offer_list"
    )  # Redirect after successful update

    def form_valid(self, form):
        response = super().form_valid(form)

        offer = form.instance
        applicable_products = offer.applicable_products.all()
        for product in applicable_products:
            discounted_price = product.rprice * (
                1 - offer.discount_percentage / 100
            )
            product.price = discounted_price
            product.save()

        return response


class OfferDetailView(DetailView):
    model = Offer
    template_name = "admin/offer_detail.html"


class OfferDeleteView(DeleteView):
    model = Offer
    template_name = "admin/offer_confirm_delete.html"
    success_url = reverse_lazy(
        "offer_list"
    )  # Redirect after successful deletion

    def form_valid(self, form):
        offer = self.get_object()
        applicable_products = offer.applicable_products.all()
        for product in applicable_products:
            product.price = (
                product.rprice
            )  # Assuming rprice is the original price
            product.save()

        return super().form_valid(form)
