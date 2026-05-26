"""
python manage.py seed_data
Creates superuser, employees, customers, products, orders, articles etc.
At least 10 products as required.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import date, timedelta
import random

from shop.models import (
    ProductType, Manufacturer, Author, Product,
    Supplier, Supply, SupplyItem,
    Employee, Customer,
    Order, OrderItem, Promo, PickupPoint,
    Article, CompanyInfo, FAQ, Contact, Vacancy, Review,
)


class Command(BaseCommand):
    help = "Seed database with demo data (≥10 products)"

    def handle(self, *args, **options):
        self.stdout.write("🌱 Seeding database...")

        # ─── Superuser ──────────────────────────────────────────────────────
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@bookstore.by", "admin123")
            self.stdout.write("  ✓ Superuser: admin / admin123")

        # ─── Product types ───────────────────────────────────────────────────
        types_data = [
            "Художественная литература", "Фантастика", "Детективы",
            "Учебники", "Биографии", "Психология", "История",
        ]
        types = {}
        for name in types_data:
            t, _ = ProductType.objects.get_or_create(name=name)
            types[name] = t
        self.stdout.write(f"  ✓ {len(types)} product types")

        # ─── Manufacturers ───────────────────────────────────────────────────
        manufacturers_data = [
            ("АСТ", "Россия"),
            ("Эксмо", "Россия"),
            ("Питер", "Россия"),
            ("Росмэн", "Россия"),
            ("Речь", "Россия"),
        ]
        manufacturers = {}
        for name, country in manufacturers_data:
            m, _ = Manufacturer.objects.get_or_create(
                name=name, defaults={"country": country}
            )
            manufacturers[name] = m
        self.stdout.write(f"  ✓ {len(manufacturers)} manufacturers")

        # ─── Authors ─────────────────────────────────────────────────────────
        authors_data = [
            ("Фёдор", "Достоевский", date(1821, 11, 11)),
            ("Лев", "Толстой", date(1828, 9, 9)),
            ("Михаил", "Булгаков", date(1891, 5, 15)),
            ("Александр", "Пушкин", date(1799, 6, 6)),
            ("Джордж", "Оруэлл", date(1903, 6, 25)),
            ("Стивен", "Кинг", date(1947, 9, 21)),
            ("Агата", "Кристи", date(1890, 9, 15)),
            ("Харуки", "Мураками", date(1949, 1, 12)),
        ]
        authors = []
        for first, last, bd in authors_data:
            a, _ = Author.objects.get_or_create(
                first_name=first, last_name=last,
                defaults={"birth_date": bd, "bio": f"Известный писатель {last}."}
            )
            authors.append(a)
        self.stdout.write(f"  ✓ {len(authors)} authors")

        # ─── Products (≥10) ──────────────────────────────────────────────────
        products_data = [
            ("Преступление и наказание", "ART-001", "Художественная литература",
             "АСТ", Decimal("12.50"), authors[0], "978-5-17-119548-3", 672, 2020),
            ("Война и мир", "ART-002", "Художественная литература",
             "Эксмо", Decimal("29.90"), authors[1], "978-5-699-20870-2", 1408, 2019),
            ("Мастер и Маргарита", "ART-003", "Художественная литература",
             "АСТ", Decimal("15.00"), authors[2], "978-5-17-090038-3", 480, 2021),
            ("Евгений Онегин", "ART-004", "Художественная литература",
             "Речь", Decimal("8.50"), authors[3], "978-5-9268-2765-5", 240, 2018),
            ("1984", "ART-005", "Фантастика",
             "АСТ", Decimal("11.90"), authors[4], "978-5-17-103182-5", 320, 2022),
            ("Скотный двор", "ART-006", "Фантастика",
             "АСТ", Decimal("9.50"), authors[4], "978-5-17-103183-2", 128, 2022),
            ("Оно", "ART-007", "Детективы",
             "Эксмо", Decimal("24.90"), authors[5], "978-5-04-098232-3", 1376, 2020),
            ("Сияние", "ART-008", "Детективы",
             "Эксмо", Decimal("16.50"), authors[5], "978-5-04-094327-0", 608, 2021),
            ("Убийство в Восточном экспрессе", "ART-009", "Детективы",
             "Эксмо", Decimal("10.90"), authors[6], "978-5-04-101236-4", 304, 2020),
            ("Норвежский лес", "ART-010", "Художественная литература",
             "Питер", Decimal("13.50"), authors[7], "978-5-4461-1684-2", 384, 2021),
            ("Идиот", "ART-011", "Художественная литература",
             "АСТ", Decimal("14.00"), authors[0], "978-5-17-119549-0", 672, 2021),
            ("Братья Карамазовы", "ART-012", "Художественная литература",
             "Эксмо", Decimal("22.00"), authors[0], "978-5-699-91717-4", 896, 2019),
        ]

        products = []
        for title, article, ptype, mfr, price, author, isbn, pages, year in products_data:
            p, created = Product.objects.get_or_create(
                article=article,
                defaults={
                    "title": title,
                    "product_type": types[ptype],
                    "manufacturer": manufacturers[mfr],
                    "price": price,
                    "isbn": isbn,
                    "pages": pages,
                    "year": year,
                    "stock": random.randint(5, 50),
                    "description": f"Известная книга «{title}».",
                    "is_active": True,
                }
            )
            if created:
                p.authors.add(author)
            products.append(p)
        self.stdout.write(f"  ✓ {len(products)} products")

        # ─── Supplier ────────────────────────────────────────────────────────
        sup, _ = Supplier.objects.get_or_create(
            name="ОптКнига",
            defaults={
                "address": "г. Минск, ул. Немига, 5",
                "phone": "+375 (17) 200-00-01",
                "email": "opt@kniga.by",
            }
        )
        for p in products[:6]:
            sup.products.add(p)

        supply, _ = Supply.objects.get_or_create(
            supplier=sup,
            date=date(2025, 1, 15),
            defaults={"total_price": Decimal("500.00"), "note": "Первая поставка 2025"}
        )
        for p in products[:3]:
            SupplyItem.objects.get_or_create(
                supply=supply, product=p,
                defaults={"quantity": 20, "unit_price": p.price * Decimal("0.7")}
            )
        self.stdout.write("  ✓ Supplier + supply")

        # ─── Employee user ────────────────────────────────────────────────────
        emp_user, _ = User.objects.get_or_create(
            username="employee1",
            defaults={"email": "emp@bookstore.by", "is_staff": True}
        )
        if _:
            emp_user.set_password("emp12345")
            emp_user.save()

        emp, _ = Employee.objects.get_or_create(
            user=emp_user,
            defaults={
                "first_name": "Иван",
                "last_name": "Петров",
                "patronymic": "Сергеевич",
                "birth_date": date(1990, 5, 20),
                "phone": "+375 (29) 111-22-33",
                "email": "emp@bookstore.by",
                "position": "Менеджер",
            }
        )
        self.stdout.write("  ✓ Employee: employee1 / emp12345")

        # ─── Customers ───────────────────────────────────────────────────────
        customers_data = [
            ("buyer1", "Анна", "Иванова", date(1992, 3, 15), "+375 (29) 555-11-22", "Минск"),
            ("buyer2", "Пётр", "Сидоров", date(1988, 7, 10), "+375 (33) 444-55-66", "Гомель"),
            ("buyer3", "Мария", "Козлова", date(1995, 12, 1), "+375 (44) 777-88-99", "Брест"),
        ]
        customer_objs = []
        for username, fn, ln, bd, phone, city in customers_data:
            u, created = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@mail.by"}
            )
            if created:
                u.set_password("buyer123")
                u.save()
            c, _ = Customer.objects.get_or_create(
                user=u,
                defaults={
                    "first_name": fn, "last_name": ln,
                    "birth_date": bd, "phone": phone,
                    "email": u.email, "city": city,
                }
            )
            customer_objs.append(c)
        self.stdout.write(f"  ✓ {len(customer_objs)} customers (password: buyer123)")

        # ─── Promos ───────────────────────────────────────────────────────────
        Promo.objects.get_or_create(
            code="WELCOME10",
            defaults={
                "discount_percent": 10,
                "status": "active",
                "valid_until": date(2026, 12, 31),
                "description": "Скидка для новых покупателей",
            }
        )
        Promo.objects.get_or_create(
            code="SUMMER20",
            defaults={
                "discount_percent": 20,
                "status": "active",
                "valid_until": date(2025, 8, 31),
                "description": "Летняя акция",
            }
        )
        Promo.objects.get_or_create(
            code="OLD2024",
            defaults={
                "discount_percent": 15,
                "status": "archived",
                "description": "Промокод 2024 года",
            }
        )
        self.stdout.write("  ✓ 3 promos")

        # ─── Pickup points ────────────────────────────────────────────────────
        PickupPoint.objects.get_or_create(
            name="ПВЗ Центр",
            defaults={
                "address": "г. Минск, пр. Независимости, 10",
                "phone": "+375 (17) 300-00-01",
                "working_hours": "Пн–Пт 9:00–20:00, Сб 10:00–18:00",
            }
        )
        PickupPoint.objects.get_or_create(
            name="ПВЗ Восток",
            defaults={
                "address": "г. Минск, ул. Козлова, 25",
                "phone": "+375 (17) 300-00-02",
                "working_hours": "Пн–Вс 10:00–21:00",
            }
        )

        # ─── Orders ───────────────────────────────────────────────────────────
        statuses = ["paid", "delivered", "shipped", "new"]
        for i, customer in enumerate(customer_objs):
            for j in range(3):
                order = Order.objects.create(
                    customer=customer,
                    employee=emp,
                    status=statuses[(i + j) % len(statuses)],
                    delivery_date=date.today() + timedelta(days=random.randint(1, 14)),
                )
                selected = random.sample(products, k=random.randint(1, 3))
                for prod in selected:
                    OrderItem.objects.create(
                        order=order,
                        product=prod,
                        quantity=random.randint(1, 2),
                        unit_price=prod.price,
                    )
        self.stdout.write("  ✓ 9 orders created")

        # ─── Articles ─────────────────────────────────────────────────────────
        articles_data = [
            ("Топ-10 книг 2025 года", "Лучшие книги этого года по версии нашего магазина."),
            ("Новое поступление классики", "Пополнили ассортимент классической литературы."),
            ("Скидки на детективы", "Весь раздел детективов — со скидкой 15% до конца месяца."),
            ("Харуки Мураками — новинка", "Ждём поступление нового романа Мураками в апреле."),
        ]
        for title, summary in articles_data:
            Article.objects.get_or_create(
                title=title,
                defaults={
                    "summary": summary,
                    "content": summary + " Подробности в нашем магазине. Следите за обновлениями.",
                    "author": emp,
                    "is_published": True,
                }
            )
        self.stdout.write("  ✓ 4 articles")

        # ─── Company info ─────────────────────────────────────────────────────
        CompanyInfo.objects.get_or_create(
            title="О нашем магазине",
            defaults={
                "content": "BookStore — книжный магазин с широким ассортиментом литературы для всей семьи.",
                "year": 2015,
                "legal_name": "ООО «Книжный мир»",
                "inn": "190123456",
            }
        )

        # ─── FAQ ──────────────────────────────────────────────────────────────
        faqs_data = [
            ("Что такое ISBN?", "ISBN — международный стандартный книжный номер, уникальный идентификатор книги."),
            ("Как оформить возврат?", "Возврат книги возможен в течение 14 дней при сохранении товарного вида."),
            ("Есть ли электронные книги?", "Пока мы продаём только печатные издания, e-book раздел в разработке."),
            ("Как использовать промокод?", "Введите код в поле 'Промокод' при оформлении заказа."),
        ]
        for q, a in faqs_data:
            FAQ.objects.get_or_create(question=q, defaults={"answer": a})
        self.stdout.write("  ✓ 4 FAQs")

        # ─── Contacts ─────────────────────────────────────────────────────────
        Contact.objects.get_or_create(
            employee=emp,
            defaults={
                "role_description": "Приём заказов, консультации по ассортименту",
                "phone": "+375 (29) 111-22-33",
                "email": "emp@bookstore.by",
            }
        )

        # ─── Vacancies ────────────────────────────────────────────────────────
        Vacancy.objects.get_or_create(
            title="Менеджер по продажам",
            defaults={
                "description": "Консультирование клиентов, оформление заказов, работа с CRM.",
                "salary_from": Decimal("800.00"),
                "salary_to": Decimal("1200.00"),
                "is_open": True,
                "posted_by": emp,
            }
        )
        Vacancy.objects.get_or_create(
            title="Специалист по закупкам",
            defaults={
                "description": "Работа с поставщиками, контроль остатков, анализ спроса.",
                "salary_from": Decimal("900.00"),
                "salary_to": Decimal("1400.00"),
                "is_open": True,
                "posted_by": emp,
            }
        )

        # ─── Reviews ──────────────────────────────────────────────────────────
        reviews_texts = [
            (5, "Отличный магазин! Быстрая доставка и хороший выбор."),
            (4, "Хороший ассортимент, нашёл редкую книгу. Рекомендую."),
            (5, "Заказываю постоянно, никогда не подводили."),
            (3, "Немного долгая доставка, но книги в отличном состоянии."),
        ]
        for customer, (rating, text) in zip(customer_objs, reviews_texts[:len(customer_objs)]):
            Review.objects.get_or_create(
                customer=customer,
                defaults={"rating": rating, "text": text}
            )
        self.stdout.write("  ✓ Reviews")

        self.stdout.write(self.style.SUCCESS("\n✅ Database seeded successfully!"))
        self.stdout.write("  Admin:    admin / admin123")
        self.stdout.write("  Employee: employee1 / emp12345")
        self.stdout.write("  Buyers:   buyer1, buyer2, buyer3 / buyer123")
