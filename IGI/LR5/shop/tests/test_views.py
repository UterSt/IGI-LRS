"""
Tests for shop views — access control, CRUD, search.
"""

from decimal import Decimal
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from shop.models import (
    ProductType, Manufacturer, Product,
    Customer, Employee, Order, OrderItem, Promo,
    Article, FAQ, Review,
)


def make_user(username, password="pass123", is_staff=False, is_superuser=False):
    u = User.objects.create_user(username, password=password, is_staff=is_staff)
    u.is_superuser = is_superuser
    u.save()
    return u


def make_customer(user):
    return Customer.objects.create(
        user=user, first_name="Test", last_name="User",
        email=f"{user.username}@test.by",
        birth_date=date(1995, 1, 1),
    )


def make_product(article="P-001", price="10.00", stock=5):
    pt, _ = ProductType.objects.get_or_create(name="Тест")
    return Product.objects.create(
        title=f"Книга {article}", article=article,
        product_type=pt, price=Decimal(price), stock=stock
    )


# ─── Public views ────────────────────────────────────────────────────────────

class TestPublicViews(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_200(self):
        r = self.client.get(reverse("shop:home"))
        self.assertEqual(r.status_code, 200)

    def test_catalogue_200(self):
        r = self.client.get(reverse("shop:catalogue"))
        self.assertEqual(r.status_code, 200)

    def test_about_200(self):
        r = self.client.get(reverse("shop:about"))
        self.assertEqual(r.status_code, 200)

    def test_news_list_200(self):
        r = self.client.get(reverse("shop:news_list"))
        self.assertEqual(r.status_code, 200)

    def test_glossary_200(self):
        r = self.client.get(reverse("shop:glossary"))
        self.assertEqual(r.status_code, 200)

    def test_contacts_200(self):
        r = self.client.get(reverse("shop:contacts"))
        self.assertEqual(r.status_code, 200)

    def test_privacy_200(self):
        r = self.client.get(reverse("shop:privacy"))
        self.assertEqual(r.status_code, 200)

    def test_vacancies_200(self):
        r = self.client.get(reverse("shop:vacancies"))
        self.assertEqual(r.status_code, 200)

    def test_promos_200(self):
        r = self.client.get(reverse("shop:promos"))
        self.assertEqual(r.status_code, 200)

    def test_reviews_200(self):
        r = self.client.get(reverse("shop:reviews"))
        self.assertEqual(r.status_code, 200)

    def test_books_api_search_200(self):
        r = self.client.get(reverse("shop:books_api_search"))
        self.assertEqual(r.status_code, 200)

    def test_currency_200(self):
        r = self.client.get(reverse("shop:currency_rates"))
        self.assertEqual(r.status_code, 200)


# ─── Product detail ───────────────────────────────────────────────────────────

class TestProductViews(TestCase):
    def setUp(self):
        self.product = make_product()

    def test_product_detail_200(self):
        r = self.client.get(reverse("shop:product_detail", args=[self.product.pk]))
        self.assertEqual(r.status_code, 200)

    def test_inactive_product_404(self):
        self.product.is_active = False
        self.product.save()
        r = self.client.get(reverse("shop:product_detail", args=[self.product.pk]))
        self.assertEqual(r.status_code, 404)


# ─── Access control ───────────────────────────────────────────────────────────

class TestAccessControl(TestCase):
    def setUp(self):
        self.anon = Client()
        self.buyer_user = make_user("buyer_ac")
        self.buyer = make_customer(self.buyer_user)
        self.buyer_client = Client()
        self.buyer_client.login(username="buyer_ac", password="pass123")

        self.staff_user = make_user("staff_ac", is_staff=True)
        self.staff_client = Client()
        self.staff_client.login(username="staff_ac", password="pass123")

        self.super_user = make_user("super_ac", is_staff=True, is_superuser=True)
        self.super_client = Client()
        self.super_client.login(username="super_ac", password="pass123")

    def test_cart_requires_login(self):
        r = self.anon.get(reverse("shop:cart"))
        self.assertRedirects(r, "/accounts/login/?next=/cart/", fetch_redirect_response=False)

    def test_cabinet_requires_login(self):
        r = self.anon.get(reverse("shop:cabinet"))
        self.assertEqual(r.status_code, 302)

    def test_product_create_requires_staff(self):
        r = self.buyer_client.get(reverse("shop:product_create"))
        self.assertEqual(r.status_code, 302)

    def test_staff_can_access_product_create(self):
        r = self.staff_client.get(reverse("shop:product_create"))
        self.assertEqual(r.status_code, 200)

    def test_statistics_requires_superuser(self):
        r = self.staff_client.get(reverse("shop:statistics"))
        self.assertEqual(r.status_code, 302)

    def test_superuser_can_access_statistics(self):
        r = self.super_client.get(reverse("shop:statistics"))
        self.assertEqual(r.status_code, 200)

    def test_api_products_requires_login(self):
        r = self.anon.get(reverse("shop:api_products"))
        self.assertEqual(r.status_code, 302)

    def test_api_products_returns_json(self):
        make_product("API-001")
        r = self.buyer_client.get(reverse("shop:api_products"))
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertIn("products", data)


# ─── Product CRUD ─────────────────────────────────────────────────────────────

class TestProductCRUD(TestCase):
    def setUp(self):
        self.staff = make_user("staff_crud", is_staff=True)
        self.c = Client()
        self.c.login(username="staff_crud", password="pass123")
        self.pt = ProductType.objects.create(name="Жанр")

    def test_create_product(self):
        r = self.c.post(reverse("shop:product_create"), {
            "title": "Новая книга",
            "article": "NEW-001",
            "price": "15.00",
            "stock": "10",
            "unit": "шт.",
            "is_active": True,
        })
        self.assertTrue(Product.objects.filter(article="NEW-001").exists())

    def test_update_product(self):
        p = make_product("UPD-001")
        r = self.c.post(reverse("shop:product_update", args=[p.pk]), {
            "title": "Обновлённая книга",
            "article": "UPD-001",
            "price": "20.00",
            "stock": "5",
            "unit": "шт.",
            "is_active": True,
        })
        p.refresh_from_db()
        self.assertEqual(p.title, "Обновлённая книга")

    def test_delete_product(self):
        p = make_product("DEL-001")
        pk = p.pk
        self.c.post(reverse("shop:product_delete", args=[pk]))
        self.assertFalse(Product.objects.filter(pk=pk).exists())


# ─── Cart ─────────────────────────────────────────────────────────────────────

class TestCart(TestCase):
    def setUp(self):
        self.user = make_user("cart_user")
        make_customer(self.user)
        self.c = Client()
        self.c.login(username="cart_user", password="pass123")
        self.product = make_product("CART-001")

    def test_add_to_cart(self):
        r = self.c.post(reverse("shop:cart_add", args=[self.product.pk]))
        session_cart = self.c.session.get("cart", {})
        self.assertIn(str(self.product.pk), session_cart)

    def test_remove_from_cart(self):
        self.c.post(reverse("shop:cart_add", args=[self.product.pk]))
        self.c.post(reverse("shop:cart_remove", args=[self.product.pk]))
        session_cart = self.c.session.get("cart", {})
        self.assertNotIn(str(self.product.pk), session_cart)


# ─── Search ───────────────────────────────────────────────────────────────────

class TestSearch(TestCase):
    def setUp(self):
        make_product("SRCH-001", price="5.00")
        p2 = make_product("SRCH-002", price="50.00")
        p2.title = "Дорогая книга"
        p2.save()

    def test_search_by_title(self):
        r = self.client.get(reverse("shop:catalogue"), {"q": "Дорогая"})
        self.assertContains(r, "Дорогая книга")

    def test_filter_by_price_max(self):
        r = self.client.get(reverse("shop:catalogue"), {"price_max": "10.00"})
        self.assertContains(r, "SRCH-001")
        self.assertNotContains(r, "Дорогая книга")

    def test_filter_by_price_min(self):
        r = self.client.get(reverse("shop:catalogue"), {"price_min": "30.00"})
        self.assertContains(r, "Дорогая книга")


# ─── Reviews ──────────────────────────────────────────────────────────────────

class TestReviews(TestCase):
    def setUp(self):
        self.user = make_user("reviewer")
        self.customer = make_customer(self.user)
        self.c = Client()
        self.c.login(username="reviewer", password="pass123")

    def test_post_review(self):
        r = self.c.post(reverse("shop:reviews"), {
            "rating": 5,
            "text": "Очень хороший магазин, советую всем!",
        })
        self.assertEqual(Review.objects.filter(customer=self.customer).count(), 1)

    def test_short_review_rejected(self):
        r = self.c.post(reverse("shop:reviews"), {
            "rating": 3,
            "text": "Ок",
        })
        self.assertEqual(Review.objects.filter(customer=self.customer).count(), 0)


# ─── Registration ────────────────────────────────────────────────────────────

class TestRegistration(TestCase):
    def test_register_creates_user_and_customer(self):
        r = self.client.post(reverse("accounts:register"), {
            "username": "newuser",
            "email": "new@test.by",
            "password1": "StrongPass99!",
            "password2": "StrongPass99!",
            "first_name": "Новый",
            "last_name": "Юзер",
            "birth_date": "1995-06-15",
        })
        self.assertTrue(User.objects.filter(username="newuser").exists())
        u = User.objects.get(username="newuser")
        self.assertTrue(hasattr(u, "customer_profile"))

    def test_minor_rejected(self):
        r = self.client.post(reverse("accounts:register"), {
            "username": "minor",
            "email": "minor@test.by",
            "password1": "StrongPass99!",
            "password2": "StrongPass99!",
            "first_name": "Юный",
            "last_name": "Пользователь",
            "birth_date": "2015-01-01",
        })
        self.assertFalse(User.objects.filter(username="minor").exists())
