"""
Views for Variant 11 – Book Store

URL patterns use both path() and re_path() with regex.
Access control:
  - superuser (admin): statistics, supply management, all data
  - employee: orders, customers, suppliers
  - customer (registered): cart, personal cabinet, purchases, promos
  - anonymous: catalogue, articles, promos, static pages
"""

import logging
import calendar
from datetime import datetime, date
import ipaddress
from decimal import Decimal
from statistics import mean, median, mode, StatisticsError

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import (
    Sum, Count, Avg, Q, F,
)
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    Product, ProductType, Manufacturer, Author,
    Supplier, Supply, SupplyItem,
    Employee, Customer,
    Order, OrderItem, Promo, PickupPoint,
    Article, CompanyInfo, FAQ, Contact, Vacancy, Review,
)
from .forms import (
    ProductForm, OrderForm, ReviewForm,
    CustomerProfileForm, ProductSearchForm, PromoApplyForm,
)
from .services import (
    get_exchange_rates,
    convert_price_byn,
    get_currency_factor,
    get_nbrb_currency_options,
    get_ipinfo_lite,
)

logger = logging.getLogger("shop")


# ─── Helpers ─────────────────────────────────────────────────────────────────

def is_employee(user):
    return user.is_authenticated and (
        user.is_staff or hasattr(user, "employee_profile")
    )


def is_superuser(user):
    return user.is_superuser


def get_customer_or_none(user):
    if not user.is_authenticated:
        return None
    return getattr(user, "customer_profile", None)


def user_timezone_info(request):
    """Return dict with timezone / date info for templates."""
    now_utc = timezone.now()
    now_local = timezone.localtime(now_utc)
    tz_name = getattr(request, "browser_timezone", None) or timezone.get_current_timezone_name()
    return {
        "now_utc": now_utc,
        "now_local": now_local,
        "tz_name": tz_name,
        "calendar_text": calendar.month(now_local.year, now_local.month),
        "today_fmt": now_local.strftime("%d/%m/%Y"),
    }


# ─── Static pages ────────────────────────────────────────────────────────────

def home(request):
    """Main page — latest published article + featured products."""
    latest_article = Article.objects.filter(is_published=True).first()
    featured = Product.objects.filter(is_active=True).order_by("-created_at")[:6]
    ctx = {
        "latest_article": latest_article,
        "featured": featured,
        **user_timezone_info(request),
    }
    return render(request, "shop/home.html", ctx)


def about(request):
    info_list = CompanyInfo.objects.all().order_by("year")
    return render(request, "shop/about.html", {"info_list": info_list})


def news_list(request):
    articles = Article.objects.filter(is_published=True)
    paginator = Paginator(articles, 6)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "shop/news_list.html", {"page_obj": page})


def news_detail(request, pk):
    article = get_object_or_404(Article, pk=pk, is_published=True)
    return render(request, "shop/news_detail.html", {"article": article})


def glossary(request):
    faqs = FAQ.objects.all()
    return render(request, "shop/glossary.html", {"faqs": faqs})


def contacts(request):
    contacts_qs = Contact.objects.select_related("employee").all()
    return render(request, "shop/contacts.html", {"contacts": contacts_qs})


def privacy(request):
    return render(request, "shop/privacy.html")


def vacancies(request):
    vacancies_qs = Vacancy.objects.filter(is_open=True)
    return render(request, "shop/vacancies.html", {"vacancies": vacancies_qs})


def promo_list(request):
    active_promos = Promo.objects.filter(status=Promo.STATUS_ACTIVE)
    archived_promos = Promo.objects.filter(status=Promo.STATUS_ARCHIVED)
    return render(request, "shop/promos.html", {
        "active_promos": active_promos,
        "archived_promos": archived_promos,
    })


def reviews_list(request):
    reviews = Review.objects.select_related("customer").all()
    customer = get_customer_or_none(request.user)
    form = ReviewForm()

    if request.method == "POST":
        if not customer:
            messages.warning(request, "Войдите в аккаунт, чтобы оставить отзыв.")
            return redirect("accounts:login")
        form = ReviewForm(request.POST)
        if form.is_valid():
            rev = form.save(commit=False)
            rev.customer = customer
            rev.save()
            messages.success(request, "Отзыв добавлен!")
            logger.info("New review from customer %s", customer)
            return redirect("shop:reviews")

    return render(request, "shop/reviews.html", {
        "reviews": reviews,
        "form": form,
        "customer": customer,
    })


# ─── Catalogue ───────────────────────────────────────────────────────────────

def catalogue(request):
    """Product list with search, filter by type/price, sort."""
    form = ProductSearchForm(request.GET)
    products = Product.objects.filter(is_active=True).select_related(
        "product_type", "manufacturer"
    )

    selected_currency = request.session.get("selected_currency", "BYN")
    currency_factor = get_currency_factor(selected_currency)

    if form.is_valid():
        q = form.cleaned_data.get("q")
        pt = form.cleaned_data.get("product_type")
        p_min = form.cleaned_data.get("price_min")
        p_max = form.cleaned_data.get("price_max")
        sort = form.cleaned_data.get("sort") or "title"

        if q:
            products = products.filter(
                Q(title__icontains=q)
                | Q(article__icontains=q)
                | Q(isbn__icontains=q)
                | Q(authors__last_name__icontains=q)
                | Q(authors__first_name__icontains=q)
            ).distinct()
        if pt:
            products = products.filter(product_type_id=pt)
        if p_min is not None:
            products = products.filter(price__gte=(p_min / currency_factor))
        if p_max is not None:
            products = products.filter(price__lte=(p_max / currency_factor))
        products = products.order_by(sort)

    paginator = Paginator(products, 12)
    page = paginator.get_page(request.GET.get("page"))
    types = ProductType.objects.all()
    return render(request, "shop/catalogue.html", {
        "page_obj": page,
        "form": form,
        "types": types,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)

    return render(request, "shop/product_detail.html", {
        "product": product,
    })


# ─── IPinfo / timezone page ───────────────────────────────────────────────────

def books_api_search(request):
    """Page that demonstrates user timezone detection and optional IPinfo data."""
    entered_ip = (request.GET.get("ip") or "").strip()
    current_ip = entered_ip or (request.META.get("REMOTE_ADDR") or "").strip()

    ip_error = None
    ipinfo_preview = {}
    ipinfo_organization = "—"

    if current_ip:
        try:
            ipaddress.ip_address(current_ip)
            ipinfo_preview = get_ipinfo_lite(current_ip)
            if isinstance(ipinfo_preview, dict):
                for key in ("org", "as_name", "as_domain"):
                    value = ipinfo_preview.get(key)
                    if isinstance(value, str) and value.strip():
                        ipinfo_organization = value.strip()
                        break
                else:
                    company = ipinfo_preview.get("company")
                    if isinstance(company, dict):
                        for key in ("name", "domain"):
                            value = company.get(key)
                            if isinstance(value, str) and value.strip():
                                ipinfo_organization = value.strip()
                                break
        except ValueError:
            ip_error = f"Некорректный IP-адрес: {current_ip}"
    else:
        ip_error = "Введите IP-адрес или откройте страницу с доступного адреса."

    now_utc = timezone.now()
    now_local = timezone.localtime(now_utc)
    today_local = timezone.localdate()

    return render(request, "shop/books_api_search.html", {
        "browser_timezone": getattr(request, "browser_timezone", None) or timezone.get_current_timezone_name(),
        "now_utc": now_utc,
        "now_local": now_local,
        "today_fmt": today_local.strftime("%d/%m/%Y"),
        "calendar_text": calendar.month(today_local.year, today_local.month),
        "ipinfo_preview": ipinfo_preview,
        "ipinfo_organization": ipinfo_organization,
        "ip_query": entered_ip,
        "resolved_ip": current_ip,
        "ip_error": ip_error,
    })


# ─── Currency API page ────────────────────────────────────────────────────────

def currency_rates(request):
    rates = get_nbrb_currency_options()
    return render(request, "shop/currency_rates.html", {"rates": rates})


@require_POST
def set_currency(request):
    """Store selected display currency in session."""
    selected = (request.POST.get("currency") or "BYN").strip().upper()
    valid_codes = {item["code"] for item in get_nbrb_currency_options()}
    if selected not in valid_codes:
        selected = "BYN"
    request.session["selected_currency"] = selected
    request.session.modified = True
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or "shop:home"
    return redirect(next_url)


# ─── CRUD – Product (admin/employee only) ────────────────────────────────────

@user_passes_test(is_employee)
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        product = form.save()
        logger.info("Product created: %s by %s", product, request.user)
        messages.success(request, f"Товар «{product.title}» добавлен.")
        return redirect("shop:product_detail", pk=product.pk)
    return render(request, "shop/product_form.html", {"form": form, "action": "Добавить"})


@user_passes_test(is_employee)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        logger.info("Product updated: %s by %s", product, request.user)
        messages.success(request, "Товар обновлён.")
        return redirect("shop:product_detail", pk=product.pk)
    return render(request, "shop/product_form.html", {"form": form, "action": "Редактировать", "product": product})


@user_passes_test(is_employee)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        title = product.title
        product.delete()
        logger.warning("Product deleted: %s by %s", title, request.user)
        messages.success(request, f"Товар «{title}» удалён.")
        return redirect("shop:catalogue")
    return render(request, "shop/product_confirm_delete.html", {"product": product})


# ─── Orders ──────────────────────────────────────────────────────────────────

@login_required
def cart(request):
    """Session-based cart."""
    cart_items = request.session.get("cart", {})
    products = Product.objects.filter(pk__in=cart_items.keys(), is_active=True)
    items = []
    total = Decimal("0")
    for product in products:
        qty = cart_items.get(str(product.pk), 0)
        subtotal = product.price * qty
        total += subtotal
        items.append({"product": product, "qty": qty, "subtotal": subtotal})
    return render(request, "shop/cart.html", {"items": items, "total": total})


@login_required
@require_POST
def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    cart = request.session.get("cart", {})
    key = str(pk)
    cart[key] = cart.get(key, 0) + 1
    request.session["cart"] = cart
    messages.success(request, f"«{product.title}» добавлен в корзину.")
    return redirect(request.META.get("HTTP_REFERER", "shop:catalogue"))


@login_required
@require_POST
def cart_remove(request, pk):
    cart = request.session.get("cart", {})
    cart.pop(str(pk), None)
    request.session["cart"] = cart
    return redirect("shop:cart")


@login_required
def checkout(request):
    customer = get_customer_or_none(request.user)
    if not customer:
        messages.warning(request, "Заполните профиль покупателя перед оформлением заказа.")
        return redirect("accounts:profile")

    cart_items = request.session.get("cart", {})
    if not cart_items:
        messages.warning(request, "Корзина пуста.")
        return redirect("shop:cart")

    promo_form = PromoApplyForm(request.POST or None, prefix="promo")
    order_form = OrderForm(request.POST or None)

    if request.method == "POST" and order_form.is_valid():
        order = order_form.save(commit=False)
        order.customer = customer

        # Apply promo
        if promo_form.is_valid():
            code = promo_form.cleaned_data["code"]
            promo = Promo.objects.get(code=code)
            order.promo = promo

        order.save()

        # Create order items
        products = Product.objects.filter(pk__in=cart_items.keys())
        for product in products:
            qty = cart_items.get(str(product.pk), 1)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                unit_price=product.price,
            )
            # Decrease stock
            product.stock = max(0, product.stock - qty)
            product.save(update_fields=["stock"])

        request.session["cart"] = {}
        logger.info("Order #%s created by %s", order.pk, request.user)
        messages.success(request, f"Заказ #{order.pk} оформлен!")
        return redirect("shop:order_detail", pk=order.pk)

    return render(request, "shop/checkout.html", {
        "order_form": order_form,
        "promo_form": promo_form,
        "cart_items": cart_items,
    })


@login_required
def order_detail(request, pk):
    customer = get_customer_or_none(request.user)
    if request.user.is_staff:
        order = get_object_or_404(Order, pk=pk)
    else:
        if not customer:
            return redirect("shop:home")
        order = get_object_or_404(Order, pk=pk, customer=customer)
    return render(request, "shop/order_detail.html", {"order": order})


# ─── Personal cabinet ─────────────────────────────────────────────────────────

@login_required
def cabinet(request):
    customer = get_customer_or_none(request.user)
    orders = []
    if customer:
        orders = Order.objects.filter(customer=customer).prefetch_related("items__product")
    return render(request, "shop/cabinet.html", {
        "customer": customer,
        "orders": orders,
        **user_timezone_info(request),
    })


# ─── Employee dashboard ───────────────────────────────────────────────────────

@user_passes_test(is_employee)
def employee_dashboard(request):
    orders = Order.objects.select_related("customer").order_by("-sale_date")[:50]
    customers = Customer.objects.all()
    supplies = Supply.objects.select_related("supplier").order_by("-date")[:20]
    return render(request, "shop/employee_dashboard.html", {
        "orders": orders,
        "customers": customers,
        "supplies": supplies,
    })


# ─── Statistics (superuser) ───────────────────────────────────────────────────

@user_passes_test(is_superuser)
def statistics(request):
    selected_currency = request.session.get("selected_currency", "BYN")
    currency_factor = get_currency_factor(selected_currency)

    # Products sorted alphabetically
    products_alpha = Product.objects.filter(is_active=True).order_by("title")

    # Total sales sum
    total_sales_byn = OrderItem.objects.aggregate(
        total=Sum(F("quantity") * F("unit_price"))
    )["total"] or Decimal("0")
    total_sales = total_sales_byn * currency_factor

    # Sales per product type
    sales_by_type = (
        OrderItem.objects
        .values("product__product_type__name")
        .annotate(total=Sum(F("quantity") * F("unit_price")), count=Sum("quantity"))
        .order_by("-total")
    )
    sales_by_type = [
        {
            **row,
            "total": row["total"] * currency_factor if row["total"] is not None else Decimal("0"),
        }
        for row in sales_by_type
    ]

    # Most / least popular products
    popular = (
        OrderItem.objects
        .values("product__title")
        .annotate(sold=Sum("quantity"))
        .order_by("-sold")[:5]
    )
    unpopular = (
        OrderItem.objects
        .values("product__title")
        .annotate(sold=Sum("quantity"))
        .order_by("sold")[:5]
    )

    # Monthly sales (current year)
    current_year = timezone.localdate().year
    monthly_sales = (
        OrderItem.objects
        .filter(order__sale_date__year=current_year)
        .values("order__sale_date__month")
        .annotate(total=Sum(F("quantity") * F("unit_price")))
        .order_by("order__sale_date__month")
    )
    monthly_labels = [calendar.month_abbr[r["order__sale_date__month"]] for r in monthly_sales]
    monthly_values = [float((r["total"] or Decimal("0")) * currency_factor) for r in monthly_sales]

    # Statistical metrics on sales per order
    order_totals = [
        float(o.total_price) * float(currency_factor)
        for o in Order.objects.prefetch_related("items").all()
    ]
    stats = {}
    if order_totals:
        stats["mean"] = round(mean(order_totals), 2)
        stats["median"] = round(median(order_totals), 2)
        try:
            stats["mode"] = round(mode(order_totals), 2)
        except StatisticsError:
            stats["mode"] = "—"

    # Customer age stats
    customers = Customer.objects.exclude(birth_date=None)
    today = timezone.localdate()
    ages = [
        today.year - c.birth_date.year - (
            (today.month, today.day) < (c.birth_date.month, c.birth_date.day)
        )
        for c in customers
    ]
    age_stats = {}
    if ages:
        age_stats["mean"] = round(mean(ages), 1)
        age_stats["median"] = round(median(ages), 1)

    return render(request, "shop/statistics.html", {
        "products_alpha": products_alpha,
        "total_sales": total_sales,
        "sales_by_type": sales_by_type,
        "popular": popular,
        "unpopular": unpopular,
        "monthly_labels": monthly_labels,
        "monthly_values": monthly_values,
        "stats": stats,
        "age_stats": age_stats,
        **user_timezone_info(request),
    })


# ─── API endpoint (requires auth) ─────────────────────────────────────────────

@login_required
def api_products(request):
    """JSON endpoint for products — requires authentication."""
    products = Product.objects.filter(is_active=True).values(
        "pk", "title", "article", "price", "stock"
    )
    return JsonResponse({"products": list(products)})
