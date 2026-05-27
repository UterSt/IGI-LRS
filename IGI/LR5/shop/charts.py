"""
charts.py — Server-side chart generation via matplotlib.

Each function returns an HttpResponse with content_type="image/png".
URLs map to these views; templates reference them via <img src="{% url ... %}".

Charts implemented:
  - chart_monthly       Bar chart: monthly sales (current year)
  - chart_by_type       Pie chart: sales by product type
  - chart_trend         Line chart: 24-month history + linear trend + 6-month forecast
  - chart_annual        Bar chart: annual revenue report (all years)
"""

import io
import calendar
from collections import OrderedDict
from decimal import Decimal

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch

from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.db.models import Sum, Count, F

from .models import OrderItem, Order
from .services import get_currency_factor

# ── palette ────────────────────────────────────────────────────────────────────
BLUE   = "#0d6efd"
GREEN  = "#198754"
RED    = "#dc3545"
ORANGE = "#fd7e14"
PURPLE = "#6f42c1"
TEAL   = "#20c997"
COLORS = [BLUE, GREEN, RED, ORANGE, PURPLE, TEAL,
          "#ffc107", "#0dcaf0", "#6c757d", "#d63384"]

FONT_FAMILY = "DejaVu Sans"

plt.rcParams.update({
    "font.family": FONT_FAMILY,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.facecolor": "white",
    "axes.facecolor": "#f8f9fa",
})


# ── helpers ────────────────────────────────────────────────────────────────────

def _get_currency(request):
    code = request.session.get("selected_currency", "BYN")
    return code, get_currency_factor(code)


def _png_response(fig):
    """Render figure to PNG bytes and return HttpResponse."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type="image/png")


def _is_superuser(user):
    return user.is_superuser


# ── 1. Monthly sales bar chart ─────────────────────────────────────────────────
#plot monthly
@user_passes_test(_is_superuser)
def chart_monthly(request):
    currency, factor = _get_currency(request)
    current_year = timezone.localdate().year

    qs = (
        OrderItem.objects
        .filter(order__sale_date__year=current_year)
        .values("order__sale_date__month")
        .annotate(total=Sum(F("quantity") * F("unit_price")))
        .order_by("order__sale_date__month")
    )

    labels = [calendar.month_abbr[r["order__sale_date__month"]] for r in qs]
    values = [float((r["total"] or Decimal("0")) * factor) for r in qs]

    fig, ax = plt.subplots(figsize=(9, 4))
    if labels:
        bars = ax.bar(labels, values, color=BLUE, alpha=0.85, width=0.6, zorder=3)
        ax.bar_label(bars, fmt="%.0f", padding=3, fontsize=8)
    else:
        ax.text(0.5, 0.5, "Нет данных за текущий год",
                ha="center", va="center", transform=ax.transAxes, fontsize=12)

    ax.set_title(f"Ежемесячные продажи {current_year}, {currency}", fontsize=13, pad=12)
    ax.set_ylabel(currency)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    fig.tight_layout()
    return _png_response(fig)


# ── 2. Sales by product type — pie chart ──────────────────────────────────────
#plot type
@user_passes_test(_is_superuser)
def chart_by_type(request):
    currency, factor = _get_currency(request)

    qs = (
        OrderItem.objects
        .values("product__product_type__name")
        .annotate(total=Sum(F("quantity") * F("unit_price")))
        .order_by("-total")
    )

    labels = [r["product__product_type__name"] or "Без категории" for r in qs]
    values = [float((r["total"] or Decimal("0")) * factor) for r in qs]

    fig, ax = plt.subplots(figsize=(7, 5))
    if values:
        wedges, texts, autotexts = ax.pie(
            values,
            labels=None,
            autopct=lambda p: f"{p:.1f}%" if p > 3 else "",
            colors=COLORS[:len(values)],
            startangle=140,
            wedgeprops={"linewidth": 0.8, "edgecolor": "white"},
        )
        for at in autotexts:
            at.set_fontsize(8)
        ax.legend(
            wedges, [f"{l} ({v:,.0f} {currency})" for l, v in zip(labels, values)],
            loc="lower center", bbox_to_anchor=(0.5, -0.18),
            ncol=2, fontsize=8, frameon=False,
        )
    else:
        ax.text(0.5, 0.5, "Нет данных", ha="center", va="center",
                transform=ax.transAxes, fontsize=12)

    ax.set_title(f"Продажи по категориям ({currency})", fontsize=13, pad=10)
    fig.tight_layout()
    return _png_response(fig)


# ── 3. Linear trend + forecast line chart ─────────────────────────────────────
#plot trend
@user_passes_test(_is_superuser)
def chart_trend(request):
    currency, factor = _get_currency(request)
    today_d = timezone.localdate()

    # Build ordered 24-month window
    month_map = OrderedDict()
    for delta in range(23, -1, -1):
        total_months = today_d.year * 12 + today_d.month - 1 - delta
        yr = total_months // 12
        mo = total_months % 12 + 1
        month_map[(yr, mo)] = 0.0

    qs = (
        OrderItem.objects
        .values("order__sale_date__year", "order__sale_date__month")
        .annotate(total=Sum(F("quantity") * F("unit_price")))
    )
    for row in qs:
        key = (row["order__sale_date__year"], row["order__sale_date__month"])
        if key in month_map:
            month_map[key] = float((row["total"] or Decimal("0")) * factor)

    trend_keys = list(month_map.keys())
    trend_y    = list(month_map.values())
    n          = len(trend_y)
    trend_x    = list(range(n))

    x_labels = [f"{calendar.month_abbr[k[1]]}\n{k[0]}" for k in trend_keys]

    # OLS linear regression
    x_mean = sum(trend_x) / n
    y_mean = sum(trend_y) / n
    num    = sum((trend_x[i] - x_mean) * (trend_y[i] - y_mean) for i in range(n))
    den    = sum((trend_x[i] - x_mean) ** 2 for i in range(n))
    a = num / den if den else 0.0
    b = y_mean - a * x_mean

    trend_line = [a * xi + b for xi in trend_x]

    # 6-month forecast
    last_key = trend_keys[-1]
    fc_labels, fc_values = [], []
    for i in range(1, 7):
        total_months = last_key[0] * 12 + last_key[1] - 1 + i
        fy = total_months // 12
        fm = total_months % 12 + 1
        fc_labels.append(f"{calendar.month_abbr[fm]}\n{fy}")
        fc_values.append(max(0.0, a * (n - 1 + i) + b))

    all_x_labels = x_labels + fc_labels
    all_x        = list(range(len(all_x_labels)))
    hist_x       = all_x[:n]
    fc_x         = all_x[n:]
    full_trend_x = all_x
    full_trend_y = [a * xi + b for xi in full_trend_x]

    # Ticks: show every 3rd label
    tick_indices = [i for i in range(len(all_x_labels)) if i % 3 == 0]
    tick_labels  = [all_x_labels[i] for i in tick_indices]

    fig, ax = plt.subplots(figsize=(12, 5))

    # Actual history area + line
    ax.fill_between(hist_x, trend_y, alpha=0.15, color=BLUE)
    ax.plot(hist_x, trend_y, color=BLUE, linewidth=2,
            marker="o", markersize=4, label="Фактические продажи")

    # Linear trend (full range)
    ax.plot(full_trend_x, full_trend_y, color=RED, linewidth=1.8,
            linestyle="--", label=f"Линейный тренд  (y = {a:.2f}·x + {b:.2f})")

    # Forecast
    if fc_x:
        ax.fill_between(fc_x, fc_values, alpha=0.18, color=GREEN)
        ax.plot(fc_x, fc_values, color=GREEN, linewidth=2,
                linestyle=":", marker="*", markersize=8, label="Прогноз (6 мес.)")

    # Divider between history and forecast
    if fc_x:
        ax.axvline(x=n - 0.5, color="gray", linewidth=1, linestyle="--", alpha=0.6)
        ax.text(n - 0.4, ax.get_ylim()[1] * 0.98, "прогноз →",
                fontsize=8, color="gray", va="top")

    ax.set_xticks(tick_indices)
    ax.set_xticklabels(tick_labels, fontsize=7)
    ax.set_ylabel(currency)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.set_title(f"Линейный тренд продаж и прогноз на 6 месяцев ({currency})",
                 fontsize=13, pad=12)
    ax.legend(fontsize=9, loc="upper left")
    fig.tight_layout()
    return _png_response(fig)


# ── 4. Annual revenue bar chart ────────────────────────────────────────────────
#plot year
@user_passes_test(_is_superuser)
def chart_annual(request):
    currency, factor = _get_currency(request)

    qs = (
        OrderItem.objects
        .values("order__sale_date__year")
        .annotate(
            total=Sum(F("quantity") * F("unit_price")),
            orders_count=Count("order__id", distinct=True),
        )
        .order_by("order__sale_date__year")
    )

    labels = [str(r["order__sale_date__year"]) for r in qs]
    values = [float((r["total"] or Decimal("0")) * factor) for r in qs]
    counts = [r["orders_count"] for r in qs]

    fig, ax1 = plt.subplots(figsize=(8, 4))
    ax2 = ax1.twinx()

    x = range(len(labels))
    bars = ax1.bar(list(x), values, color=GREEN, alpha=0.8, width=0.5,
                   zorder=3, label=f"Выручка, {currency}")
    ax1.bar_label(bars, fmt="%.0f", padding=3, fontsize=8)

    ax2.plot(list(x), counts, color=ORANGE, linewidth=2,
             marker="D", markersize=6, label="Заказов")
    ax2.set_ylabel("Количество заказов", color=ORANGE)
    ax2.tick_params(axis="y", labelcolor=ORANGE)

    ax1.set_xticks(list(x))
    ax1.set_xticklabels(labels)
    ax1.set_ylabel(f"Выручка, {currency}")
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax1.set_title(f"Годовой отчёт поступлений от продаж ({currency})",
                  fontsize=13, pad=12)

    # Combined legend
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2,
               fontsize=9, loc="upper left")
    fig.tight_layout()
    return _png_response(fig)
