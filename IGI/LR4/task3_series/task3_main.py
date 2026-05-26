"""
task3_main.py — Entry point for Task 3: Extended Series with Statistics & Plot.
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Extends LR3 Task 1 (ln((x+1)/(x-1)) series) with:
  a) Statistical parameters: mean, median, mode, variance, std
  b) matplotlib plot (series vs. math reference)
  c) Save plot to file
"""

from utils import (print_separator, input_float_constrained,
                   input_positive_int, input_string_nonempty)
from task3_series.series_class    import LnRatioSeries
from task3_series.statistics_calc import Statistics
from task3_series.plotter         import SeriesPlotter


# ─────────────────────────────────────────────
#  INPUT
# ─────────────────────────────────────────────

def get_x_values() -> list[float]:
    """
    Prompt the user to enter one or more x values (|x| > 1).

    Returns:
        list[float]: List of valid x values.
    """
    n = input_positive_int("  Сколько значений x вычислить? ")
    values = []
    for i in range(n):
        x = input_float_constrained(
            prompt    = f"  x[{i+1}] (|x| > 1): ",
            condition = lambda v: abs(v) > 1,
            error_msg = "|x| должно быть > 1."
        )
        values.append(x)
    return values


def get_eps() -> float:
    """
    Prompt the user for the series precision eps > 0.

    Returns:
        float: Positive precision value.
    """
    return input_float_constrained(
        prompt    = "  Точность eps (например 0.000001): ",
        condition = lambda v: v > 0,
        error_msg = "eps должно быть положительным."
    )


# ─────────────────────────────────────────────
#  MAIN TASK ENTRY POINT
# ─────────────────────────────────────────────

def run_task3() -> None:
    """
    Main entry point for Task 3 — Extended ln Series.

    Collects user input, computes the series for multiple x values,
    shows a results table, computes descriptive statistics on F(x) values,
    plots series vs. math reference, and saves the figure.
    """
    print_separator("Задание 3 — Ряды + Статистика + График (Вариант 11)")
    print(f"  Ряд: {LnRatioSeries.get_series_name()}")
    print("  Формула: 2·Σ 1/((2n+1)·x^(2n+1)),  |x| > 1\n")

    x_values = get_x_values()
    eps      = get_eps()

    series = LnRatioSeries()
    print()
    results = series.compute_range(x_values, eps)

    if not results:
        print("  [!] Нет допустимых результатов — все значения x нарушают |x|>1.")
        return

    print(f"\n  {series}")
    print(f"  repr: {repr(series)}")
    series.print_table()

    fx_values = [r.fx for r in results]

    if len(fx_values) >= 2:
        stats = Statistics(fx_values)
        stats.print_summary("Статистика значений F(x)")
        print(f"\n  str(stats) : {stats}")
        print(f"  len(stats) : {len(stats)}")
    else:
        print("\n  [Замечание] Для статистики нужно минимум 2 точки. Пропускаем.")

    print("\n  Строим график...")
    plotter = SeriesPlotter()

    x_min = max(1.05, min(r.x for r in results) - 0.5)
    x_max = max(r.x for r in results) + 0.5

    saved = plotter.plot(results, x_min=x_min, x_max=x_max, eps=eps)
    print(f"  График сохранён: {saved}")
    print(f"  repr(plotter) : {repr(plotter)}")
