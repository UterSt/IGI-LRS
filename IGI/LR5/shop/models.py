"""
Models for Variant 11 – Book Store

Relationships:
  OneToOne  : Customer ↔ User, Employee ↔ User
  ForeignKey: Product → ProductType, Product → Manufacturer,
              OrderItem → Order, OrderItem → Product,
              Supply → Supplier, SupplyItem → Supply, SupplyItem → Product,
              Review → Customer, Article → Employee,
              Vacancy → Employee (posted_by)
  M2M       : Product ↔ Author (a book has many authors, an author has many books)
"""

import re
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import logging

logger = logging.getLogger("shop")


# ─── Validators ──────────────────────────────────────────────────────────────

#valid phone
def validate_phone_by(value: str):
    """Phone must be in format +375 (XX) XXX-XX-XX"""
    pattern = r"^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$"
    if not re.match(pattern, value):
        raise ValidationError(
            "Телефон должен быть в формате +375 (29) XXX-XX-XX"
        )

#valid age
def validate_adult(value):
    """Age must be 18+"""
    from datetime import date
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError("Возраст должен быть не менее 18 лет.")


# ─── Static / Reference tables ───────────────────────────────────────────────

class ProductType(models.Model):
    """Category / genre of a book (e.g. 'Фантастика', 'Учебники')"""
    name = models.CharField("Название категории", max_length=100, unique=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        # verbose_name
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    """Publisher / издательство"""
    name = models.CharField("Название издательства", max_length=200, unique=True)
    country = models.CharField("Страна", max_length=100, blank=True)
    website = models.URLField("Сайт", blank=True)
    phone = models.CharField(
        "Телефон", max_length=20, blank=True,
        validators=[validate_phone_by],
        help_text="+375 (29) XXX-XX-XX"
    )

    class Meta:
        verbose_name = "Издательство"
        verbose_name_plural = "Издательства"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Author(models.Model):
    """Book author (M2M with Product)"""
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    birth_date = models.DateField("Дата рождения", null=True, blank=True)
    bio = models.TextField("Биография", blank=True)

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# ─── Core product ────────────────────────────────────────────────────────────

class Product(models.Model):
    """Book / товар"""
    title = models.CharField("Название", max_length=255)
    article = models.CharField("Артикул", max_length=50, unique=True)
    # ForeignKey → ProductType (один тип — много книг)
    product_type = models.ForeignKey( #ForeignKey
        ProductType, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="products",
        verbose_name="Категория",
    )
    # ForeignKey → Manufacturer
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="products",
        verbose_name="Издательство",
    )
    # M2M → Author
    authors = models.ManyToManyField( #ManyToMany
        Author, blank=True,
        related_name="products",
        verbose_name="Авторы",
    )
    price = models.DecimalField("Цена (BYN)", max_digits=10, decimal_places=2)
    unit = models.CharField(
        "Единица измерения", max_length=20, default="шт.",
        choices=[("шт.", "штука"), ("компл.", "комплект")],
    )
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Фото", upload_to="products/", blank=True, null=True)
    isbn = models.CharField("ISBN", max_length=20, blank=True)
    pages = models.PositiveIntegerField("Страниц", null=True, blank=True)
    year = models.PositiveIntegerField("Год издания", null=True, blank=True)
    stock = models.PositiveIntegerField("На складе", default=0)
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField("Добавлен", auto_now_add=True)
    updated_at = models.DateTimeField("Изменён", auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.article})"


# ─── Supplier / Supply ────────────────────────────────────────────────────────

class Supplier(models.Model):
    """Поставщик"""
    name = models.CharField("Название", max_length=200)
    address = models.CharField("Адрес", max_length=300, blank=True)
    phone = models.CharField(
        "Телефон", max_length=20,
        validators=[validate_phone_by], #valid
        help_text="+375 (29) XXX-XX-XX",
    )
    email = models.EmailField("Email", blank=True)
    products = models.ManyToManyField(
        Product, blank=True,
        related_name="suppliers",
        verbose_name="Поставляемые товары",
    )

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Supply(models.Model):
    """Закупка у поставщика"""
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE,
        related_name="supplies",
        verbose_name="Поставщик",
    )
    date = models.DateField("Дата закупки")
    total_price = models.DecimalField(
        "Итоговая сумма", max_digits=12, decimal_places=2, default=0
    )
    note = models.TextField("Примечание", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Закупка"
        verbose_name_plural = "Закупки"
        ordering = ["-date"]

    def __str__(self):
        return f"Закупка #{self.pk} от {self.date} — {self.supplier}"


class SupplyItem(models.Model):
    """Строка закупки"""
    supply = models.ForeignKey(
        Supply, on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Закупка",
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="supply_items",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField("Количество")
    unit_price = models.DecimalField("Цена за ед.", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Позиция закупки"
        verbose_name_plural = "Позиции закупки"

    def __str__(self):
        return f"{self.product} × {self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.unit_price


# ─── Users ───────────────────────────────────────────────────────────────────

class Employee(models.Model):
    """Сотрудник — OneToOne с User"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        related_name="employee_profile",
        verbose_name="Пользователь",
    )
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    patronymic = models.CharField("Отчество", max_length=100, blank=True)
    birth_date = models.DateField("Дата рождения", validators=[validate_adult])
    phone = models.CharField(
        "Телефон", max_length=20,
        validators=[validate_phone_by],
        help_text="+375 (29) XXX-XX-XX",
    )
    email = models.EmailField("Email")
    position = models.CharField("Должность", max_length=100)
    photo = models.ImageField("Фото", upload_to="employees/", blank=True, null=True)
    description = models.TextField("Описание", blank=True)
    hired_at = models.DateField("Дата приёма", default=timezone.now)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ["last_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.position})"

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return " ".join(p for p in parts if p)


class Customer(models.Model):
    """Покупатель — OneToOne с User"""
    user = models.OneToOneField( #OneToOne
        User, on_delete=models.CASCADE,
        related_name="customer_profile",
        verbose_name="Пользователь",
    )
    first_name = models.CharField("Имя", max_length=100)
    last_name = models.CharField("Фамилия", max_length=100)
    patronymic = models.CharField("Отчество", max_length=100, blank=True)
    birth_date = models.DateField(
        "Дата рождения", validators=[validate_adult],
        null=True, blank=True,
    )
    phone = models.CharField(
        "Телефон", max_length=20, blank=True,
        validators=[validate_phone_by],
        help_text="+375 (29) XXX-XX-XX",
    )
    email = models.EmailField("Email")
    address = models.CharField("Адрес доставки", max_length=300, blank=True)
    city = models.CharField("Город", max_length=100, blank=True)
    registered_at = models.DateTimeField("Зарегистрирован", auto_now_add=True)

    class Meta:
        verbose_name = "Покупатель"
        verbose_name_plural = "Покупатели"
        ordering = ["last_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def full_name(self):
        parts = [self.last_name, self.first_name, self.patronymic]
        return " ".join(p for p in parts if p)


# ─── Orders ──────────────────────────────────────────────────────────────────

class Promo(models.Model):
    """Промокод / купон"""
    STATUS_ACTIVE = "active"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Активный"),
        (STATUS_ARCHIVED, "В архиве"),
    ]
    code = models.CharField("Код", max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField("Скидка %")
    status = models.CharField(
        "Статус", max_length=10,
        choices=STATUS_CHOICES, default=STATUS_ACTIVE,
    )
    valid_until = models.DateField("Действует до", null=True, blank=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"
        ordering = ["status", "code"]

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"

    @property
    def is_valid(self):
        if self.status != self.STATUS_ACTIVE:
            return False
        if self.valid_until and self.valid_until < timezone.localdate():
            return False
        return True


class PickupPoint(models.Model):
    """Точка самовывоза"""
    name = models.CharField("Название", max_length=200)
    address = models.CharField("Адрес", max_length=300)
    phone = models.CharField(
        "Телефон", max_length=20,
        validators=[validate_phone_by],
    )
    working_hours = models.CharField("Режим работы", max_length=100, blank=True)

    class Meta:
        verbose_name = "Точка самовывоза"
        verbose_name_plural = "Точки самовывоза"

    def __str__(self):
        return self.name


class Order(models.Model):
    """Заказ"""
    STATUS_NEW = "new"
    STATUS_PAID = "paid"
    STATUS_SHIPPED = "shipped"
    STATUS_DELIVERED = "delivered"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_NEW, "Новый"),
        (STATUS_PAID, "Оплачен"),
        (STATUS_SHIPPED, "Отправлен"),
        (STATUS_DELIVERED, "Доставлен"),
        (STATUS_CANCELLED, "Отменён"),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Покупатель",
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="orders",
        verbose_name="Сотрудник",
    )
    promo = models.ForeignKey(
        Promo, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="orders",
        verbose_name="Промокод",
    )
    pickup_point = models.ForeignKey(
        PickupPoint, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="orders",
        verbose_name="Точка самовывоза",
    )
    status = models.CharField(
        "Статус", max_length=20,
        choices=STATUS_CHOICES, default=STATUS_NEW,
    )
    sale_date = models.DateTimeField("Дата продажи", auto_now_add=True)
    delivery_date = models.DateField("Дата доставки", null=True, blank=True)
    address = models.CharField("Адрес доставки", max_length=300, blank=True)
    note = models.TextField("Примечание", blank=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-sale_date"]

    def __str__(self):
        return f"Заказ #{self.pk} — {self.customer}"

    @property
    def total_price(self):
        total = sum(item.subtotal for item in self.items.all())
        if self.promo and self.promo.is_valid:
            total = total * (1 - Decimal(self.promo.discount_percent) / Decimal(100))
        return round(total, 2)


class OrderItem(models.Model):
    """Позиция в заказе — ForeignKey к Order и Product"""
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Заказ",
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE,
        related_name="order_items",
        verbose_name="Товар",
    )
    quantity = models.PositiveIntegerField("Количество", default=1)
    unit_price = models.DecimalField("Цена за ед.", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказа"

    def __str__(self):
        return f"{self.product.title} × {self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.unit_price


# ─── Static pages content ─────────────────────────────────────────────────────

class Article(models.Model):
    """Новости / статьи"""
    title = models.CharField("Заголовок", max_length=255)
    summary = models.CharField("Краткое содержание", max_length=300)
    content = models.TextField("Полный текст")
    image = models.ImageField("Картинка", upload_to="articles/", blank=True, null=True)
    static_image = models.CharField("Статичная картинка (путь)", max_length=100, blank=True, default="")
    author = models.ForeignKey(
        Employee, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="articles",
        verbose_name="Автор",
    )
    published_at = models.DateTimeField("Дата публикации", auto_now_add=True)
    is_published = models.BooleanField("Опубликовано", default=True)

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


class CompanyInfo(models.Model):
    """О компании"""
    title = models.CharField("Заголовок", max_length=200)
    content = models.TextField("Текст о компании")
    logo = models.ImageField("Логотип", upload_to="company/", blank=True, null=True)
    video_url = models.URLField("Видео (URL)", blank=True)
    year = models.PositiveIntegerField("Год события", null=True, blank=True)
    legal_name = models.CharField("Юридическое название", max_length=200, blank=True)
    inn = models.CharField("УНП", max_length=20, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Информация о компании"
        verbose_name_plural = "Информация о компании"

    def __str__(self):
        return self.title


class FAQ(models.Model):
    """Словарь терминов и понятий"""
    question = models.CharField("Вопрос / термин", max_length=300)
    answer = models.TextField("Ответ / определение")
    added_at = models.DateField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = "Термин / FAQ"
        verbose_name_plural = "Словарь терминов"
        ordering = ["-added_at"]

    def __str__(self):
        return self.question


class Contact(models.Model):
    """Контакты сотрудников"""
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE,
        related_name="contact",
        verbose_name="Сотрудник",
    )
    role_description = models.CharField("Описание работ", max_length=200)
    photo = models.ImageField("Фото", upload_to="contacts/", blank=True, null=True)
    phone = models.CharField(
        "Телефон", max_length=20,
        validators=[validate_phone_by],
    )
    email = models.EmailField("Email")

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

    def __str__(self):
        return str(self.employee)


class Vacancy(models.Model):
    """Вакансии"""
    title = models.CharField("Должность", max_length=200)
    description = models.TextField("Описание вакансии")
    salary_from = models.DecimalField(
        "Зарплата от", max_digits=10, decimal_places=2,
        null=True, blank=True,
    )
    salary_to = models.DecimalField(
        "Зарплата до", max_digits=10, decimal_places=2,
        null=True, blank=True,
    )
    is_open = models.BooleanField("Открыта", default=True)
    posted_by = models.ForeignKey(
        Employee, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="vacancies",
        verbose_name="Опубликовал",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


#Отзыв
class Review(models.Model):
    """Отзывы"""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Покупатель",
    )
    rating = models.PositiveSmallIntegerField(
        "Оценка", choices=RATING_CHOICES, default=5
    )
    text = models.TextField("Текст отзыва")
    created_at = models.DateTimeField("Дата", auto_now_add=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Отзыв от {self.customer} ({self.rating}★)"
