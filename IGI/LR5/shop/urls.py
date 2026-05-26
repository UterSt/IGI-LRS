"""
URL patterns for shop app.
Uses both path() and re_path() with regex as required.
"""

from django.urls import path, re_path
from . import views

app_name = "shop"

urlpatterns = [
    # ─── Static pages ──────────────────────────────────────────────────────
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contacts/", views.contacts, name="contacts"),
    path("privacy/", views.privacy, name="privacy"),
    path("vacancies/", views.vacancies, name="vacancies"),
    path("glossary/", views.glossary, name="glossary"),
    path("reviews/", views.reviews_list, name="reviews"),
    path("promos/", views.promo_list, name="promos"),

    # ─── News (re_path with regex) ─────────────────────────────────────────
    path("news/", views.news_list, name="news_list"),
    # pk must be a positive integer (\d+)
    re_path(r"^news/(?P<pk>\d+)/$", views.news_detail, name="news_detail"),

    # ─── Catalogue ─────────────────────────────────────────────────────────
    path("catalogue/", views.catalogue, name="catalogue"),
    # Product pk — regex ensures only digits
    re_path(r"^catalogue/(?P<pk>\d+)/$", views.product_detail, name="product_detail"),
    path("catalogue/create/", views.product_create, name="product_create"),
    re_path(r"^catalogue/(?P<pk>\d+)/edit/$", views.product_update, name="product_update"),
    re_path(r"^catalogue/(?P<pk>\d+)/delete/$", views.product_delete, name="product_delete"),

    # ─── External API pages ────────────────────────────────────────────────
    path("books-search/", views.books_api_search, name="books_api_search"),
    path("currency/", views.currency_rates, name="currency_rates"),
    path("currency/set/", views.set_currency, name="set_currency"),

    # ─── Cart & Orders ─────────────────────────────────────────────────────
    path("cart/", views.cart, name="cart"),
    re_path(r"^cart/add/(?P<pk>\d+)/$", views.cart_add, name="cart_add"),
    re_path(r"^cart/remove/(?P<pk>\d+)/$", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    re_path(r"^orders/(?P<pk>\d+)/$", views.order_detail, name="order_detail"),

    # ─── Personal cabinet & dashboards ────────────────────────────────────
    path("cabinet/", views.cabinet, name="cabinet"),
    path("dashboard/", views.employee_dashboard, name="employee_dashboard"),
    path("statistics/", views.statistics, name="statistics"),

    # ─── JSON API (auth required) ──────────────────────────────────────────
    path("api/products/", views.api_products, name="api_products"),
]
