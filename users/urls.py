"""
URL configuration for WoodsLand project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from __future__ import annotations

from django.urls import path

from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    # path('send_otp/', views.send_otp_view, name='send-otp'),
    # path('otp_verification/', views.otp_verification_view, name='otp-verification'),
    path("", views.home, name="home"),
    path("store", views.store, name="store"),
    path("search/", views.search, name="search"),
    path("about", views.about, name="about"),
    path("contact", views.contact, name="contact"),
    path("register", views.register, name="register"),
    path("login/otp/", views.verify_otp, name="verify_otp"),
    # path('login/',views.userLogin, name="user-login"),
    # path('login/otp/',views.otpLogin, name="otp-login"),
    path("login/", views.custom_login, name="login"),
    path("logout", views.custom_logout, name="logout"),
    path("resetPassword/", views.resetPassword, name="resetPassword"),
    path("forgotPassword/", views.forgotPassword, name="forgotPassword"),
    path(
        "resetpassword_validate/<uidb64>/<token>/",
        views.resetpassword_validate,
        name="resetpassword_validate",
    ),
    path("user_profile/", views.user_profile, name="user_profile"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("/<str:order_number>/", views.order_details, name="order_details"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("received_orders/", views.received_orders, name="received_orders"),
    path("returned_orders/", views.returned_orders, name="returned_orders"),
    path("addresses/", views.view_address, name="addresses"),
    path("add_address/", views.add_address, name="add_address"),
    path("addresses/edit/<slug:id>/", views.edit_address, name="edit_address"),
    path(
        "addresses/delete/<slug:id>/",
        views.delete_address,
        name="delete_address",
    ),
    path(
        "addresses/set_default/<slug:id>/",
        views.set_default,
        name="set_default",
    ),
    path("admin_dashboard", views.admin_dashboard, name="admin_dashboard"),
    path(
        "download-order-data/",
        views.download_order_data,
        name="download_order_data",
    ),
    path("order_management", views.order_management, name="order_management"),
    path(
        "update_order_status/<str:order_number>/",
        views.update_order_status,
        name="update_order_status",
    ),
    path("admin_user_view", views.admin_user_view, name="admin_user_view"),
    path("admin_login", views.admin_login, name="admin_login"),
    path("admin_logout", views.admin_logout, name="admin_logout"),
    path("admin_home", views.admin_home, name="admin_home"),
    path("admin_user_block", views.admin_user_block, name="admin_user_block"),
    path(
        "admin_product_view",
        views.admin_product_view,
        name="admin_product_view",
    ),
    path(
        "admin_product_add", views.admin_product_add, name="admin_product_add"
    ),
    path(
        "admin_product_delete",
        views.admin_product_delete,
        name="admin_product_delete",
    ),
    path(
        "admin_category_view",
        views.admin_category_view,
        name="admin_category_view",
    ),
    path(
        "admin_category_add",
        views.admin_category_add,
        name="admin_category_add",
    ),
    path(
        "admin_category_edit",
        views.admin_category_edit,
        name="admin_category_edit",
    ),
    path(
        "admin_category_delete",
        views.admin_category_delete,
        name="admin_category_delete",
    ),
    # path("store", views.store, name="store"),
    path("<slug:category_slug>/", views.store, name="product_by_category"),
    path("product_details", views.product_details, name="product_details"),
    path(
        "<slug:category_slug>/<slug:product_slug>/",
        views.product_details,
        name="product_details",
    ),
    path(
        "admin_product_update/<int:product_id>",
        views.admin_product_update,
        name="admin_product_update",
    ),
    path(
        "product_variations/add/<int:product_id>/",
        views.add_product_variation,
        name="add_product_variation",
    ),
    path(
        "product_variations/edit/<int:variation_id>/",
        views.edit_product_variation,
        name="edit_product_variation",
    ),
    path(
        "product_variations/<int:product_id>",
        views.product_variations_view,
        name="product_variations",
    ),
    path(
        "product_variations/delete/<int:variation_id>/",
        views.delete_product_variation,
        name="delete_product_variation",
    ),
]
