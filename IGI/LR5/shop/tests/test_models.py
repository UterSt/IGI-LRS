"""
Tests for shop models — validators, properties, relationships.
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from shop.models import (
    ProductType, Manufacturer, Author, Product,
    Customer, Employee, Order, OrderItem, Promo,
    validate_phone_by, validate_adult,
)


# ─── Validator tests ─────────────────────────────────────────────────────────

class TestPhoneValidator(TestCase):
    def test_valid_phone(self):
        """Valid BY phone should not raise."""
        validate_phone_by("+375 (29) 123-45-67")

    @pytest.mark.parametrize("phone", [
        "80291234567",
        "+375291234567",
        "+375 29 123-45-67",
        "375 (29) 123-45-67",
        "",
    ])
    def test_invalid_phones(self):
        invalid = ["80291234567", "+375291234567", "+375 29 123-45-67", "375 (29) 123-45-67"]
        for phone in invalid:
            with self.assertRaises(ValidationError):
                validate_phone_by(phone)

    def test_empty_phone_raises(self):
        with self.assertRaises(ValidationError):
            validate_phone_by("not-a-phone")


class TestAdultValidator(TestCase):
    def test_adult_passes(self):
        bd = date.today().replace(year=date.today().year - 20)
        validate_adult(bd)

    def test_minor_raises(self):
        bd = date.today() - timedelta(days=17 * 365)
        with self.assertRaises(ValidationError):
            validate_adult(bd)

    def test_exactly_18_passes(self):
        bd = date.today().replace(year=date.today().year - 18)
        validate_adult(bd)


# ─── Product tests ────────────────────────────────────────────────────────────

class TestProduct(TestCase):
    def setUp(self):
        self.pt = ProductType.objects.create(name="Тест-тип")
        self.mfr = Manufacturer.objects.create(name="Тест-изд")
        self.product = Product.objects.create(
            title="Тестовая книга",
            article="TEST-001",
            product_type=self.pt,
            manufacturer=self.mfr,
            price=Decimal("10.00"),
            stock=5,
        )

    def test_str(self):
        self.assertIn("Тестовая книга", str(self.product))
        self.assertIn("TEST-001", str(self.product))

    def test_default_active(self):
        self.assertTrue(self.product.is_active)

    def test_article_unique(self):
        from django.db import IntegrityError
        with self.assertRaises(Exception):
            Product.objects.create(
                title="Дубль", article="TEST-001", price=Decimal("5.00")
            )

    def test_authors_m2m(self):
        author = Author.objects.create(first_name="А", last_name="Б")
        self.product.authors.add(author)
        self.assertIn(author, self.product.authors.all())


# ─── Customer tests ───────────────────────────────────────────────────────────

class TestCustomer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testcust", password="pass")
        self.customer = Customer.objects.create(
            user=self.user,
            first_name="Иван",
            last_name="Тестов",
            patronymic="Петрович",
            email="test@test.by",
            birth_date=date(1990, 1, 1),
        )

    def test_full_name(self):
        self.assertEqual(self.customer.full_name, "Тестов Иван Петрович")

    def test_str(self):
        self.assertIn("Тестов", str(self.customer))

    def test_one_to_one(self):
        self.assertEqual(self.user.customer_profile, self.customer)


# ─── Promo tests ──────────────────────────────────────────────────────────────

class TestPromo(TestCase):
    def test_active_valid_promo(self):
        promo = Promo(
            code="TEST10",
            discount_percent=10,
            status=Promo.STATUS_ACTIVE,
            valid_until=date.today() + timedelta(days=30),
        )
        self.assertTrue(promo.is_valid)

    def test_archived_promo_invalid(self):
        promo = Promo(
            code="OLD10",
            discount_percent=10,
            status=Promo.STATUS_ARCHIVED,
        )
        self.assertFalse(promo.is_valid)

    def test_expired_promo_invalid(self):
        promo = Promo(
            code="EXP10",
            discount_percent=10,
            status=Promo.STATUS_ACTIVE,
            valid_until=date.today() - timedelta(days=1),
        )
        self.assertFalse(promo.is_valid)


# ─── Order + OrderItem tests ──────────────────────────────────────────────────

class TestOrder(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("buyer", password="pass")
        self.customer = Customer.objects.create(
            user=self.user,
            first_name="Анна",
            last_name="Покупатель",
            email="buyer@test.by",
            birth_date=date(1995, 5, 5),
        )
        self.product = Product.objects.create(
            title="Книга", article="BK-001", price=Decimal("20.00"), stock=10
        )
        self.order = Order.objects.create(customer=self.customer)
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            unit_price=Decimal("20.00"),
        )

    def test_total_price_no_promo(self):
        self.assertEqual(self.order.total_price, Decimal("40.00"))

    def test_total_price_with_promo(self):
        from datetime import timedelta
        promo = Promo.objects.create(
            code="TEST20",
            discount_percent=20,
            status=Promo.STATUS_ACTIVE,
            valid_until=date.today() + timedelta(days=10),
        )
        self.order.promo = promo
        self.order.save()
        self.assertEqual(self.order.total_price, Decimal("32.00"))

    def test_order_str(self):
        self.assertIn(str(self.order.pk), str(self.order))

    def test_order_item_subtotal(self):
        item = self.order.items.first()
        self.assertEqual(item.subtotal, Decimal("40.00"))
