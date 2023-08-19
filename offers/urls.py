from __future__ import annotations

from django.urls import path

from .views import BannerImageCreateView
from .views import BannerImageDeleteView
from .views import BannerImageListView
from .views import BannerImageUpdateView
from .views import OfferCreateView
from .views import OfferDeleteView
from .views import OfferDetailView
from .views import OfferListView
from .views import OfferUpdateView

urlpatterns = [
    path("add", BannerImageCreateView.as_view(), name="add_banner_image"),
    path(
        "edit/<int:pk>/",
        BannerImageUpdateView.as_view(),
        name="edit_banner_image",
    ),
    path(
        "delete/<int:pk>/",
        BannerImageDeleteView.as_view(),
        name="delete_banner_image",
    ),
    path("list", BannerImageListView.as_view(), name="product_banner_list"),
    path("offers/list/", OfferListView.as_view(), name="offer_list"),
    path("offers/add/", OfferCreateView.as_view(), name="offer_create"),
    path(
        "offers/<int:pk>/edit/", OfferUpdateView.as_view(), name="offer_edit"
    ),
    path("offers/<int:pk>/", OfferDetailView.as_view(), name="offer_detail"),
    path(
        "offers/<int:pk>/delete/",
        OfferDeleteView.as_view(),
        name="offer_delete",
    ),
]
