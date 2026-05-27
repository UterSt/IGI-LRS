"""
Management command: python manage.py seed_news

Creates 10 published news articles with auto-generated placeholder images
(coloured rectangles with title text, rendered via Pillow).

Usage:
    python manage.py seed_news            # add if count < 10
    python manage.py seed_news --force    # delete existing and recreate
"""

import io
import random
import textwrap
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.utils import timezone

ARTICLES = [
    {
        "title": "BookStore открывает новый филиал в Минске",
        "summary": "Компания BookStore рада сообщить об открытии нового магазина в центре Минска.",
        "content": (
            "BookStore открывает двери нового флагманского магазина на проспекте Независимости, 25. "
            "Здесь вас ждут более 15 000 наименований книг на русском, белорусском и иностранных языках, "
            "уютная читальная зона и еженедельные встречи с авторами. "
            "Открытие состоится 1 июня — приходите, вход свободный!\n\n"
            "В честь открытия все покупатели получат скидку 10% на первую покупку и бесплатный кофе."
        ),
    },
    {
        "title": "Топ-10 книг этого лета",
        "summary": "Наши редакторы составили список must-read книг на предстоящее лето.",
        "content": (
            "Лето — лучшее время читать. Мы собрали десятку книг, которые покорили читателей в этом сезоне:\n\n"
            "1. «Алхимик» — Пауло Коэльо\n"
            "2. «Мастер и Маргарита» — Михаил Булгаков\n"
            "3. «1984» — Джордж Оруэлл\n"
            "4. «Маленький принц» — Антуан де Сент-Экзюпери\n"
            "5. «Гарри Поттер и философский камень» — Дж. К. Роулинг\n"
            "6. «Преступление и наказание» — Фёдор Достоевский\n"
            "7. «Великий Гэтсби» — Фрэнсис Скотт Фицджеральд\n"
            "8. «Сто лет одиночества» — Габриэль Гарсиа Маркес\n"
            "9. «Война и мир» — Лев Толстой\n"
            "10. «Дюна» — Фрэнк Герберт\n\n"
            "Все книги доступны в нашем каталоге с доставкой по всей Беларуси."
        ),
    },
    {
        "title": "Встреча с автором: Виктор Мартинович",
        "summary": "10 июня в нашем магазине пройдёт встреча с белорусским писателем Виктором Мартиновичем.",
        "content": (
            "Виктор Мартинович — один из самых ярких голосов современной белорусской литературы. "
            "Автор романов «Мова», «Паранойя», «Ночь», «Сфагнум» и других. "
            "На встрече писатель расскажет о своём новом романе, ответит на вопросы читателей "
            "и подпишет книги.\n\n"
            "Начало в 18:00. Вход по предварительной регистрации — ссылка на сайте магазина."
        ),
    },
    {
        "title": "Скидки до 30% на классику мировой литературы",
        "summary": "Весь июнь классические произведения продаются со скидкой до 30%.",
        "content": (
            "BookStore объявляет летнюю акцию: скидки до 30% на произведения классической мировой литературы. "
            "В акции участвуют книги Толстого, Достоевского, Чехова, Шекспира, Гёте, Диккенса и многих других.\n\n"
            "Акция действует с 1 по 30 июня. Чтобы воспользоваться скидкой, добавьте книгу в корзину "
            "и используйте промокод CLASSIC2026."
        ),
    },
    {
        "title": "Новое поступление: детективы и триллеры",
        "summary": "В наш каталог поступило более 200 новых детективов и триллеров от ведущих издательств.",
        "content": (
            "Любители острых сюжетов — порадуйтесь! На прошлой неделе мы получили масштабное пополнение каталога: "
            "более 200 новых книг в жанрах детектив, триллер и криминальная драма.\n\n"
            "Среди новинок — последние романы Харлана Кобена, Донны Тарт, Стига Ларссона, "
            "а также дебютные работы молодых белорусских авторов. "
            "Ищите раздел «Детективы» на странице каталога."
        ),
    },
    {
        "title": "BookStore запускает программу лояльности",
        "summary": "Теперь каждая покупка приносит баллы, которые можно обменять на скидку.",
        "content": (
            "BookStore запускает обновлённую программу лояльности «Книжный клуб».\n\n"
            "Как это работает:\n"
            "• За каждые 10 BYN покупки — 1 балл\n"
            "• 100 баллов = скидка 5 BYN на следующую покупку\n"
            "• Баллы начисляются автоматически при оформлении заказа\n"
            "• Срок действия баллов — 1 год\n\n"
            "Зарегистрированные пользователи уже могут видеть свой баланс в личном кабинете."
        ),
    },
    {
        "title": "Детская книжная ярмарка в BookStore",
        "summary": "15 июня проводим детскую книжную ярмарку с мастер-классами и конкурсами.",
        "content": (
            "Приглашаем семьи с детьми на нашу летнюю книжную ярмарку!\n\n"
            "В программе:\n"
            "• Ярмарка детских книг со скидками до 40%\n"
            "• Мастер-класс по рисованию персонажей из любимых книг\n"
            "• Конкурс чтецов для детей от 6 до 12 лет\n"
            "• Встреча с авторами детских книг\n"
            "• Розыгрыш книжных наборов\n\n"
            "Ярмарка пройдёт 15 июня с 11:00 до 18:00 в нашем главном магазине. Вход свободный!"
        ),
    },
    {
        "title": "Как выбрать книгу в подарок: советы BookStore",
        "summary": "Наши эксперты рассказывают, как не ошибиться с выбором книги в подарок.",
        "content": (
            "Дарить книгу — прекрасная идея, но как выбрать правильную? Вот несколько советов от наших редакторов:\n\n"
            "1. Учитывайте интересы. Если человек увлекается историей — подарите историческую прозу; "
            "если любит фантастику — новинку из этого жанра.\n\n"
            "2. Спросите у знакомых. Иногда лучший источник идеи — друг или коллега получателя.\n\n"
            "3. Воспользуйтесь нашим разделом «Хиты продаж» — бестселлеры всегда в тренде.\n\n"
            "4. Подарочная упаковка. В BookStore мы красиво упакуем любую книгу бесплатно.\n\n"
            "5. Подарочный сертификат. Если совсем не уверены — сертификат BookStore решит проблему."
        ),
    },
    {
        "title": "Обзор: лучшие научно-популярные книги 2026 года",
        "summary": "Подборка самых интересных научпоп книг первой половины 2026 года.",
        "content": (
            "Наука стала интереснее, чем когда-либо, а научно-популярные книги помогают нам её понять. "
            "Вот наш обзор лучших новинок научпоп за первую половину 2026 года:\n\n"
            "«Квантовая механика для всех» — доступное объяснение самой загадочной науки.\n\n"
            "«Мозг без границ» — революционные открытия нейробиологии последних лет.\n\n"
            "«Климат: руководство пользователя» — честный взгляд на изменение климата и пути решения.\n\n"
            "«Будущее уже здесь» — как технологии ИИ меняют повседневную жизнь.\n\n"
            "Все книги уже в нашем каталоге. Читайте и познавайте мир!"
        ),
    },
    {
        "title": "BookStore теперь на маркетплейсах",
        "summary": "Наши книги теперь доступны на крупнейших белорусских маркетплейсах.",
        "content": (
            "Хорошая новость для тех, кто привык делать покупки на маркетплейсах: "
            "BookStore теперь официально представлен на крупнейших белорусских площадках.\n\n"
            "Однако напоминаем: покупая напрямую через наш сайт, вы получаете:\n"
            "• Лучшие цены (без наценки платформы)\n"
            "• Баллы программы лояльности\n"
            "• Промокоды и специальные акции\n"
            "• Прямую поддержку наших консультантов\n\n"
            "Присоединяйтесь и читайте с удовольствием!"
        ),
    },
]

# Colour palette for placeholder images
PALETTE = [
    (13, 110, 253),    # bootstrap blue
    (25, 135, 84),     # bootstrap green
    (220, 53, 69),     # bootstrap red
    (255, 193, 7),     # bootstrap yellow
    (111, 66, 193),    # bootstrap purple
    (13, 202, 240),    # bootstrap cyan
    (253, 126, 20),    # bootstrap orange
    (32, 201, 151),    # bootstrap teal
    (108, 117, 125),   # bootstrap secondary
    (214, 51, 132),    # bootstrap pink
]


def _make_placeholder_image(title: str, color_rgb: tuple) -> bytes:
    """Return PNG bytes: a solid-colour rectangle with white title text."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (800, 400), color=color_rgb)
        draw = ImageDraw.Draw(img)
        # Draw a slightly darker overlay rectangle for contrast
        r, g, b = color_rgb
        dark = (max(0, r - 40), max(0, g - 40), max(0, b - 40))
        draw.rectangle([0, 340, 800, 400], fill=dark)

        # Wrap title text
        lines = textwrap.wrap(title, width=32)
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        except Exception:
            font = ImageFont.load_default()

        total_h = len(lines) * 48
        y = (400 - total_h) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            draw.text(((800 - w) // 2, y), line, fill="white", font=font)
            y += 48

        # BookStore label at bottom
        try:
            small_font = ImageFont.truetype("DejaVuSans.ttf", 20)
        except Exception:
            small_font = font
        draw.text((20, 350), "BookStore", fill="white", font=small_font)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        # Pillow not available — return a 1×1 white pixel
        return (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\xff\xff"
            b"\x3f\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82"
        )


class Command(BaseCommand):
    help = "Seed 10 news articles with placeholder images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true",
            help="Delete existing articles and recreate all 10.",
        )

    def handle(self, *args, **options):
        from shop.models import Article

        if options["force"]:
            deleted, _ = Article.objects.all().delete()
            self.stdout.write(f"Deleted {deleted} articles.")

        existing = Article.objects.count()
        if existing >= 10 and not options["force"]:
            self.stdout.write(self.style.WARNING(
                f"Already {existing} articles exist. Use --force to recreate."
            ))
            return

        created = 0
        for i, data in enumerate(ARTICLES):
            if Article.objects.filter(title=data["title"]).exists():
                continue

            article = Article(
                title=data["title"],
                summary=data["summary"],
                content=data["content"],
                is_published=True,
            )
            # Generate placeholder image
            png_bytes = _make_placeholder_image(data["title"], PALETTE[i % len(PALETTE)])
            filename = f"news_{i + 1:02d}.png"
            article.image.save(filename, ContentFile(png_bytes), save=False)
            article.save()
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Created {created} articles. Total in DB: {Article.objects.count()}"
        ))
