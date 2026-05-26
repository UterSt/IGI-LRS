import re
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from shop.models import Customer


PHONE_PATTERN = r"^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$"


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(max_length=100, label="Имя", required=True)
    last_name = forms.CharField(max_length=100, label="Фамилия", required=True)
    patronymic = forms.CharField(max_length=100, label="Отчество", required=False)
    birth_date = forms.DateField(
        label="Дата рождения",
        widget=forms.DateInput(attrs={"type": "date"}),
        required=True,
    )
    phone = forms.CharField(
        max_length=20, label="Телефон", required=False,
        widget=forms.TextInput(attrs={
            "placeholder": "+375 (29) XXX-XX-XX",
            "pattern": r"\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}",
            "title": "Формат: +375 (29) XXX-XX-XX",
        }),
    )
    city = forms.CharField(max_length=100, label="Город", required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if phone and not re.match(PHONE_PATTERN, phone):
            raise ValidationError("Телефон должен быть в формате +375 (29) XXX-XX-XX")
        return phone

    def clean_birth_date(self):
        from datetime import date
        bd = self.cleaned_data.get("birth_date")
        if bd:
            today = date.today()
            age = today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
            if age < 18:
                raise ValidationError("Возраст должен быть не менее 18 лет.")
        return bd

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            Customer.objects.create(
                user=user,
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
                patronymic=self.cleaned_data.get("patronymic", ""),
                birth_date=self.cleaned_data.get("birth_date"),
                phone=self.cleaned_data.get("phone", ""),
                email=self.cleaned_data["email"],
                city=self.cleaned_data.get("city", ""),
            )
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={"autofocus": True}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(),
    )
