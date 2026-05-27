"""
services.py — external API wrappers and currency helpers.

External APIs:
  1. IPinfo Lite — optional geolocation / timezone helper
  2. NBRB API — official exchange rates without API key
"""

from __future__ import annotations

import logging
import time
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from functools import lru_cache
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger("shop")

# ─── Currency cache ──────────────────────────────────────────────────────────

_CURRENCY_CACHE: dict[str, Any] = {
    "timestamp": 0.0,
    "options": None,
    "by_code": None,
}
_CURRENCY_CACHE_TTL = 60 * 60  # 1 hour

DEFAULT_CURRENCY_OPTIONS = [
    {
        "code": "BYN",
        "name": "Белорусский рубль",
        "scale": Decimal("1"),
        "official_rate": Decimal("1"),
        "rate_per_byn": Decimal("1"),
        "byn_per_unit": Decimal("1"),
    },
    {
        "code": "USD",
        "name": "Доллар США",
        "scale": Decimal("1"),
        "official_rate": Decimal("3.2"),
        "rate_per_byn": Decimal("0.3125"),
        "byn_per_unit": Decimal("3.2"),
    },
    {
        "code": "EUR",
        "name": "Евро",
        "scale": Decimal("1"),
        "official_rate": Decimal("3.5"),
        "rate_per_byn": Decimal("0.2857"),
        "byn_per_unit": Decimal("3.5"),
    },
    {
        "code": "RUB",
        "name": "Российский рубль",
        "scale": Decimal("100"),
        "official_rate": Decimal("3.5"),
        "rate_per_byn": Decimal("28.5714"),
        "byn_per_unit": Decimal("0.035"),
    },
]


def _to_decimal(value: Any, default: str = "0") -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


def _normalize_currency_item(item: dict[str, Any]) -> dict[str, Any] | None:
    code = (
        item.get("Cur_Abbreviation")
        or item.get("Cur_Code")
        or item.get("cur_abbreviation")
        or item.get("code")
    )
    if not code:
        return None

    name = (
        item.get("Cur_Name")
        or item.get("Cur_Name_Eng")
        or item.get("Cur_Name_Bel")
        or item.get("name")
        or code
    )
    scale = _to_decimal(item.get("Cur_Scale") or item.get("scale") or 1, "1")
    official_rate = _to_decimal(
        item.get("Cur_OfficialRate")
        or item.get("rate")
        or item.get("official_rate")
        or 0,
        "0",
    )

    if official_rate <= 0 or scale <= 0:
        return None

    byn_per_unit = official_rate / scale
    rate_per_byn = Decimal("1") / byn_per_unit if byn_per_unit else Decimal("0")

    return {
        "code": str(code).upper(),
        "name": str(name),
        "scale": scale,
        "official_rate": official_rate,
        "rate_per_byn": rate_per_byn,
        "byn_per_unit": byn_per_unit,
    }


def _fetch_nbrb_currency_options() -> list[dict[str, Any]]:
    """Fetch and normalize latest NBRB exchange rates."""
    url = getattr(settings, "NBRB_RATES_URL", "https://api.nbrb.by/exrates/rates")
    params = {"periodicity": 0}
    try:
        response = requests.get(url, params=params, timeout=2)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, list):
            raise ValueError("Unexpected NBRB payload type")
    except Exception as exc:  # noqa: BLE001
        logger.warning("NBRB rates unavailable: %s", exc)
        return DEFAULT_CURRENCY_OPTIONS.copy()

    options: list[dict[str, Any]] = [
        {
            "code": "BYN",
            "name": "Белорусский рубль",
            "scale": Decimal("1"),
            "official_rate": Decimal("1"),
            "rate_per_byn": Decimal("1"),
            "byn_per_unit": Decimal("1"),
        }
    ]
    for item in payload:
        normalized = _normalize_currency_item(item)
        if normalized:
            options.append(normalized)

    # Prefer well-known currencies first, then alphabetical.
    priority = {"BYN": 0, "USD": 1, "EUR": 2, "RUB": 3}
    options.sort(key=lambda x: (priority.get(x["code"], 99), x["name"], x["code"]))
    return options


def get_nbrb_currency_options(force_refresh: bool = False) -> list[dict[str, Any]]:
    """Return cached currency catalog."""
    now = time.time()
    if (
        not force_refresh
        and _CURRENCY_CACHE["options"] is not None
        and now - float(_CURRENCY_CACHE["timestamp"] or 0) < _CURRENCY_CACHE_TTL
    ):
        return list(_CURRENCY_CACHE["options"])

    options = _fetch_nbrb_currency_options()
    by_code = {item["code"]: item for item in options}
    _CURRENCY_CACHE["timestamp"] = now
    _CURRENCY_CACHE["options"] = options
    _CURRENCY_CACHE["by_code"] = by_code
    return list(options)


def get_currency_by_code(code: str | None) -> dict[str, Any]:
    catalog = get_nbrb_currency_options()
    code = (code or "BYN").upper()
    by_code = _CURRENCY_CACHE.get("by_code") or {item["code"]: item for item in catalog}
    return by_code.get(code, by_code["BYN"])

#NBRB
def get_currency_factor(code: str | None) -> Decimal:
    """How many target currency units correspond to 1 BYN."""
    currency = get_currency_by_code(code)
    return _to_decimal(currency.get("rate_per_byn"), "1") or Decimal("1")


def convert_byn_amount(amount_byn: Any, currency_code: str | None = "BYN") -> Decimal:
    """Convert a BYN amount to selected currency using NBRB rates."""
    amount = _to_decimal(amount_byn, "0")
    factor = get_currency_factor(currency_code)
    return (amount * factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)



# ─── IPinfo (timezone / geolocation helper) ───────────────────────────────────

#IPinfo
def get_ipinfo_lite(ip_address: str | None = None) -> dict[str, Any]:
    """
    Query IPinfo Lite when an access token is configured.

    The free Lite API returns country / continent / ASN information.
    If no token is configured, the function falls back to an empty dict so
    the page still renders.
    """
    token = getattr(settings, "IPINFO_TOKEN", "")
    if not token:
        return {}

    target = (ip_address or "me").strip() or "me"
    url = f"https://api.ipinfo.io/lite/{target}"
    params = {"token": token}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict):
            return data
    except Exception as exc:  # noqa: BLE001
        logger.warning("IPinfo Lite unavailable: %s", exc)
    return {}

# ─── Google Books API ─────────────────────────────────────────────────────────

def search_google_books(query: str, max_results: int = 5) -> list[dict]:
    """
    Search Google Books API.
    Returns list of dicts: {title, authors, publisher, year, isbn, description, thumbnail}
    """
    url = settings.GOOGLE_BOOKS_API_URL
    params = {"q": query, "maxResults": max_results, "printType": "books"}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        logger.error("Google Books API error: %s", exc)
        return []

    results = []
    for item in data.get("items", []):
        info = item.get("volumeInfo", {})
        isbns = {
            id_info["type"]: id_info["identifier"]
            for id_info in info.get("industryIdentifiers", [])
            if "type" in id_info and "identifier" in id_info
        }
        results.append({
            "title": info.get("title", ""),
            "authors": ", ".join(info.get("authors", [])),
            "publisher": info.get("publisher", ""),
            "year": info.get("publishedDate", "")[:4],
            "isbn": isbns.get("ISBN_13") or isbns.get("ISBN_10", ""),
            "description": info.get("description", "")[:500],
            "thumbnail": info.get("imageLinks", {}).get("thumbnail", ""),
            "pages": info.get("pageCount"),
        })
    return results


# ─── Compatibility wrappers for existing tests ───────────────────────────────

#get NBRB
def get_exchange_rates(base: str = "EUR", symbols: str = "USD,RUB") -> dict:
    """
    Backward-compatible wrapper.
    Existing tests mock a Frankfurter-like response shape, so we support both:
    - old response: {"rates": {...}}
    - NBRB response: list of currency items
    """
    # Try the legacy path first if caller or tests expect it.
    url = getattr(settings, "FRANKFURTER_API_URL", "https://api.frankfurter.dev")
    params = {"base": base, "symbols": symbols}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:  # noqa: BLE001
        logger.error("Currency API error: %s", exc)
        return {}

    if isinstance(data, dict) and isinstance(data.get("rates"), dict):
        return data.get("rates", {})

    # Fallback: return a normalized slice from NBRB catalog if the payload is a list.
    options = get_nbrb_currency_options()
    wanted = {s.strip().upper() for s in symbols.split(",") if s.strip()}
    result = {}
    for item in options:
        code = item["code"]
        if wanted and code not in wanted:
            continue
        if code == "BYN":
            continue
        result[code] = float(item["rate_per_byn"])
    return result


def convert_price_byn(price_byn, rates: dict) -> dict:
    """
    Compatibility helper used by existing tests.
    It converts BYN to EUR and optionally USD using a rates mapping.
    """
    BYN_PER_EUR = 3.55
    eur_price = float(price_byn) / BYN_PER_EUR
    result = {"EUR": round(eur_price, 2)}
    usd_rate = rates.get("USD")
    if usd_rate:
        result["USD"] = round(eur_price * float(usd_rate), 2)
    return result
