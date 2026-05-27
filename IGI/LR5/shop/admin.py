from django.contrib import admin
from .models import (
    ProductType, Manufacturer, Author, Product,
    Supplier, Supply, SupplyItem,
    Employee, Customer,
    Order, OrderItem, Promo, PickupPoint,
    Article, CompanyInfo, FAQ, Contact, Vacancy, Review,
)


# ─── Inlines ──────────────────────────────────────────────────────────────────
#inline записи
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ("product", "quantity", "unit_price")
    readonly_fields = ()


class SupplyItemInline(admin.TabularInline):
    model = SupplyItem
    extra = 1
    fields = ("product", "quantity", "unit_price")


# ─── Product ─────────────────────────────────────────────────────────────────

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "phone", "website")
    search_fields = ("name", "country")
    list_filter = ("country",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "birth_date")
    search_fields = ("last_name", "first_name")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "title", "article", "product_type", "manufacturer",
        "price", "stock", "is_active", "created_at",
    )
    list_filter = ("product_type", "manufacturer", "is_active")
    search_fields = ("title", "article", "isbn")
    filter_horizontal = ("authors",)
    list_editable = ("price", "stock", "is_active")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Основное", {"fields": ("title", "article", "product_type", "manufacturer", "authors")}),
        ("Ценообразование", {"fields": ("price", "unit", "stock")}),
        ("Книжные данные", {"fields": ("isbn", "pages", "year")}),
        ("Описание", {"fields": ("description", "image", "is_active")}),
        ("Метаданные", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# ─── Supplier / Supply ────────────────────────────────────────────────────────

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "address")
    search_fields = ("name",)
    filter_horizontal = ("products",)


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ("pk", "supplier", "date", "total_price")
    list_filter = ("supplier", "date")
    search_fields = ("supplier__name",)
    inlines = [SupplyItemInline]
    readonly_fields = ("created_at",)


# ─── Users ────────────────────────────────────────────────────────────────────

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "position", "phone", "email", "hired_at")
    search_fields = ("last_name", "first_name", "position")
    list_filter = ("position",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "city", "registered_at")
    search_fields = ("last_name", "first_name", "email")
    list_filter = ("city",)


# ─── Orders ──────────────────────────────────────────────────────────────────

@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "status", "valid_until", "is_valid")
    list_filter = ("status",)
    search_fields = ("code",)
    list_editable = ("status",)


@admin.register(PickupPoint)
class PickupPointAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone", "working_hours")
    search_fields = ("name", "address")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "pk", "customer", "employee", "status",
        "sale_date", "delivery_date", "total_price",
    )
    list_filter = ("status", "sale_date")
    search_fields = ("customer__last_name", "customer__first_name")
    inlines = [OrderItemInline]
    readonly_fields = ("sale_date",)
    list_editable = ("status",)
    autocomplete_fields = ["customer", "employee"]


# ─── Static pages ────────────────────────────────────────────────────────────

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_at", "is_published")
    list_filter = ("is_published", "published_at")
    search_fields = ("title", "summary")
    list_editable = ("is_published",)


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ("title", "year", "updated_at")


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "added_at")
    search_fields = ("question", "answer")


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("employee", "role_description", "phone", "email")
    search_fields = ("employee__last_name",)


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "salary_from", "salary_to", "is_open", "created_at")
    list_filter = ("is_open",)
    search_fields = ("title",)
    list_editable = ("is_open",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("customer", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("customer__last_name", "text")
