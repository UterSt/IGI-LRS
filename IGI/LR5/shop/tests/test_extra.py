"""
Additional tests for accounts views and shop services
to push coverage above 80%.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from shop.models import Customer
from shop.services import (
    search_google_books, get_exchange_rates, convert_price_byn
)


# ─── Accounts views ──────────────────────────────────────────────────────────

class TestAccountsViews(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = User.objects.create_user("acct_test", password="Pass1234!")
        Customer.objects.create(
            user=self.user,
            first_name="Тест", last_name="Юзер",
            email="acct@test.by", birth_date=date(1995, 1, 1),
        )

    def test_login_page_get(self):
        r = self.c.get(reverse("accounts:login"))
        self.assertEqual(r.status_code, 200)

    def test_login_success_redirects(self):
        r = self.c.post(reverse("accounts:login"), {
            "username": "acct_test", "password": "Pass1234!"
        })
        self.assertRedirects(r, "/", fetch_redirect_response=False)

    def test_login_wrong_password(self):
        r = self.c.post(reverse("accounts:login"), {
            "username": "acct_test", "password": "wrong"
        })
        self.assertEqual(r.status_code, 200)  # stays on login

    def test_logout_redirects(self):
        self.c.login(username="acct_test", password="Pass1234!")
        r = self.c.get(reverse("accounts:logout"))
        self.assertEqual(r.status_code, 302)

    def test_register_page_get(self):
        r = self.c.get(reverse("accounts:register"))
        self.assertEqual(r.status_code, 200)

    def test_authenticated_user_redirected_from_login(self):
        self.c.login(username="acct_test", password="Pass1234!")
        r = self.c.get(reverse("accounts:login"))
        self.assertEqual(r.status_code, 302)

    def test_authenticated_user_redirected_from_register(self):
        self.c.login(username="acct_test", password="Pass1234!")
        r = self.c.get(reverse("accounts:register"))
        self.assertEqual(r.status_code, 302)

    def test_profile_get(self):
        self.c.login(username="acct_test", password="Pass1234!")
        r = self.c.get(reverse("accounts:profile"))
        self.assertEqual(r.status_code, 200)

    def test_profile_update(self):
        self.c.login(username="acct_test", password="Pass1234!")
        r = self.c.post(reverse("accounts:profile"), {
            "first_name": "Новое",
            "last_name": "Имя",
            "email": "new@test.by",
            "city": "Минск",
            "birth_date": "1995-01-01",
        })
        self.user.customer_profile.refresh_from_db()
        self.assertEqual(self.user.customer_profile.first_name, "Новое")

    def test_profile_requires_login(self):
        r = self.c.get(reverse("accounts:profile"))
        self.assertEqual(r.status_code, 302)


# ─── Services tests ───────────────────────────────────────────────────────────

class TestGoogleBooksService(TestCase):
    @patch("shop.services.requests.get")
    def test_search_returns_results(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "items": [{
                "volumeInfo": {
                    "title": "Test Book",
                    "authors": ["Test Author"],
                    "publisher": "Test Publisher",
                    "publishedDate": "2020",
                    "industryIdentifiers": [
                        {"type": "ISBN_13", "identifier": "9781234567897"}
                    ],
                    "description": "A test book description",
                    "imageLinks": {"thumbnail": "http://example.com/cover.jpg"},
                    "pageCount": 300,
                }
            }]
        }
        mock_get.return_value = mock_response
        results = search_google_books("Test Book")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Test Book")
        self.assertEqual(results[0]["isbn"], "9781234567897")

    @patch("shop.services.requests.get")
    def test_search_empty_response(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {}
        mock_get.return_value = mock_response
        results = search_google_books("nothing")
        self.assertEqual(results, [])

    @patch("shop.services.requests.get")
    def test_search_network_error_returns_empty(self, mock_get):
        import requests as req
        mock_get.side_effect = req.RequestException("timeout")
        results = search_google_books("error")
        self.assertEqual(results, [])


class TestFrankfurterService(TestCase):
    @patch("shop.services.requests.get")
    def test_get_rates_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "base": "EUR",
            "rates": {"USD": 1.08, "GBP": 0.86}
        }
        mock_get.return_value = mock_response
        rates = get_exchange_rates("EUR", "USD,GBP")
        self.assertIn("USD", rates)
        self.assertAlmostEqual(rates["USD"], 1.08)

    @patch("shop.services.requests.get")
    def test_get_rates_network_error(self, mock_get):
        import requests as req
        mock_get.side_effect = req.RequestException("error")
        rates = get_exchange_rates()
        self.assertEqual(rates, {})

    def test_convert_price_byn_with_usd(self):
        rates = {"USD": 1.08}
        result = convert_price_byn(Decimal("35.50"), rates)
        self.assertIn("EUR", result)
        self.assertIn("USD", result)
        self.assertGreater(result["EUR"], 0)
        self.assertGreater(result["USD"], 0)

    def test_convert_price_byn_no_rates(self):
        result = convert_price_byn(Decimal("20.00"), {})
        self.assertIn("EUR", result)
        self.assertNotIn("USD", result)


# ─── Views — employee / cabinet edge cases ────────────────────────────────────

class TestEmployeeDashboard(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("emp_dash", password="pass", is_staff=True)
        self.c = Client()
        self.c.login(username="emp_dash", password="pass")

    def test_employee_dashboard_200(self):
        r = self.c.get(reverse("shop:employee_dashboard"))
        self.assertEqual(r.status_code, 200)


class TestCabinetNoCustomer(TestCase):
    """Cabinet works even if no customer profile exists yet."""
    def setUp(self):
        self.user = User.objects.create_user("no_profile", password="pass")
        self.c = Client()
        self.c.login(username="no_profile", password="pass")

    def test_cabinet_without_profile(self):
        r = self.c.get(reverse("shop:cabinet"))
        self.assertEqual(r.status_code, 200)


class TestNewsDetailView(TestCase):
    def setUp(self):
        u = User.objects.create_user("news_emp", password="pass", is_staff=True)
        from shop.models import Employee, Article
        emp = Employee.objects.create(
            user=u, first_name="E", last_name="E",
            birth_date=date(1990, 1, 1),
            phone="+375 (29) 000-00-00",
            email="e@e.by", position="Ed",
        )
        self.article = Article.objects.create(
            title="Тест новость",
            summary="Краткое",
            content="Полный текст статьи.",
            author=emp,
            is_published=True,
        )

    def test_news_detail_200(self):
        r = self.client.get(reverse("shop:news_detail", args=[self.article.pk]))
        self.assertEqual(r.status_code, 200)

    def test_unpublished_news_404(self):
        self.article.is_published = False
        self.article.save()
        r = self.client.get(reverse("shop:news_detail", args=[self.article.pk]))
        self.assertEqual(r.status_code, 404)
