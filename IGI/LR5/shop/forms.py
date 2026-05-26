"""
Forms for shop app — client-side validation via HTML5 attributes,
server-side validation via Django form validators.
"""

import re
from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Product, Order, OrderItem, Review,
    Customer, Promo,
)


PHONE_PATTERN = r"^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$"


def phone_widget_attrs():
    return {
        "placeholder": "+375 (29) XXX-XX-XX",
        "pattern": r"\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}",
        "title": "Формат: +375 (29) XXX-XX-XX",
    }


# ─── Product ─────────────────────────────────────────────────────────────────

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "title", "article", "product_type", "manufacturer",
            "authors", "price", "unit", "description",
            "image", "isbn", "pages", "year", "stock", "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"min": "0"}),
            "authors": forms.CheckboxSelectMultiple(),
        }

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise ValidationError("Цена не может быть отрицательной.")
        return price

    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        if stock is not None and stock < 0:
            raise ValidationError("Количество на складе не может быть отрицательным.")
        return stock


# ─── Order ────────────────────────────────────────────────────────────────────

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["pickup_point", "address", "delivery_date", "note"]
        widgets = {
            "delivery_date": forms.DateInput(attrs={"type": "date"}),
            "note": forms.Textarea(attrs={"rows": 3}),
        }


class PromoApplyForm(forms.Form):
    code = forms.CharField(
        label="Промокод",
        max_length=50,
        widget=forms.TextInput(attrs={"placeholder": "Введите промокод"}),
    )

    def clean_code(self):
        code = self.cleaned_data["code"].strip().upper()
        try:
            promo = Promo.objects.get(code=code)
        except Promo.DoesNotExist:
            raise ValidationError("Промокод не найден.")
        if not promo.is_valid:
            raise ValidationError("Промокод недействителен или истёк.")
        return code


# ─── Review ──────────────────────────────────────────────────────────────────

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 4, "required": True, "minlength": "10"}),
            "rating": forms.Select(),
        }

    def clean_text(self):
        text = self.cleaned_data.get("text", "").strip()
        if len(text) < 10:
            raise ValidationError("Отзыв должен содержать не менее 10 символов.")
        return text


# ─── Customer profile ────────────────────────────────────────────────────────

class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "patronymic", "birth_date", "phone", "email", "address", "city"]
        widgets = {
            "birth_date": forms.DateInput(attrs={"type": "date"}),
            "phone": forms.TextInput(attrs=phone_widget_attrs()),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if phone and not re.match(PHONE_PATTERN, phone):
            raise ValidationError("Телефон должен быть в формате +375 (29) XXX-XX-XX")
        return phone


# ─── Search ──────────────────────────────────────────────────────────────────

class ProductSearchForm(forms.Form):
    q = forms.CharField(
        label="Поиск",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Название, артикул, ISBN, автор..."}),
    )
    product_type = forms.IntegerField(required=False, widget=forms.HiddenInput())
    price_min = forms.DecimalField(
        label="Цена от", required=False,
        widget=forms.NumberInput(attrs={"min": "0", "step": "0.01", "placeholder": "0.00"}),
    )
    price_max = forms.DecimalField(
        label="Цена до", required=False,
        widget=forms.NumberInput(attrs={"min": "0", "step": "0.01", "placeholder": "999.99"}),
    )
    sort = forms.ChoiceField(
        label="Сортировка",
        required=False,
        choices=[
            ("title", "Название А–Я"),
            ("-title", "Название Я–А"),
            ("price", "Цена ↑"),
            ("-price", "Цена ↓"),
            ("-created_at", "Новинки"),
        ],
    )
