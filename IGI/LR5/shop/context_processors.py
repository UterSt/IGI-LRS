import calendar

from django.utils import timezone

from .services import get_nbrb_currency_options, get_currency_by_code, get_currency_factor


def currency_context(request):
    selected_currency = request.session.get("selected_currency", "BYN")
    options = get_nbrb_currency_options()
    valid_codes = {item["code"] for item in options}
    if selected_currency not in valid_codes:
        selected_currency = "BYN"
    currency = get_currency_by_code(selected_currency)
    return {
        "currency_options": options,
        "selected_currency": selected_currency,
        "selected_currency_name": currency["name"],
        "currency_factor": get_currency_factor(selected_currency),
    }


def timezone_context(request):
    now_utc = timezone.now()
    now_local = timezone.localtime(now_utc)
    browser_timezone = getattr(request, "browser_timezone", None) or getattr(
        request,
        "active_timezone_name",
        timezone.get_current_timezone_name(),
    )
    ipinfo_preview = {}
    return {
        "browser_timezone": browser_timezone,
        "now_utc": now_utc,
        "now_local": now_local,
        "today_fmt": now_local.strftime("%d/%m/%Y"),
        "calendar_text": calendar.month(now_local.year, now_local.month),
        "ipinfo_preview": ipinfo_preview,
    }
