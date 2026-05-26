"""
task6_main.py — Entry point for Task 6: Pandas (Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Датасет: FIFA 19  (https://www.kaggle.com/datasets/karangadiya/fifa19)
Скачайте 'data.csv' и переименуйте в  LR4/data/fifa19.csv

Если файл не найден — используется синтетический датасет с той же структурой.

Задание А — Series и DataFrame:
  Создать player_sample из 5 случайных строк [Name, Age, Overall], сбросить индекс.

Задание Б — Статистический анализ:
  1. Информация о датафрейме
  2. Средняя скорость (SprintSpeed) игроков с зарплатой ниже средней
  3. Во сколько раз ShotPower самых агрессивных выше наименее агрессивных?
"""

from utils import print_separator
from task6_pandas.data_loader       import FIFADataLoader
from task6_pandas.series_dataframe  import SeriesDataFrameDemo
from task6_pandas.stats_analysis    import StatisticalAnalyzer


# ─────────────────────────────────────────────
#  MAIN TASK ENTRY POINT
# ─────────────────────────────────────────────

def run_task6() -> None:
    """
    Main entry point for Task 6 — Pandas FIFA 19 Analysis.

    Loads (or generates) the dataset, then runs
    Задание А (Series/DataFrame demos) and
    Задание Б (statistical analysis).
    """
    print_separator("Задание 6 — Pandas: FIFA 19 (Вариант 11)")

    # ── Загрузка датасета ──────────────────────────────
    print("\n  Датасет: FIFA 19")
    print("  Путь:    data/fifa19.csv")
    print("  (если файл не найден — создаётся синтетический датасет)\n")

    loader = FIFADataLoader()
    df = loader.load()

    if loader.is_synthetic:
        print("\n  ⚠ Используется СИНТЕТИЧЕСКИЙ датасет.")
        print("  Скачайте реальный: https://www.kaggle.com/datasets/karangadiya/fifa19")
        print("  и сохраните как LR4/data/fifa19.csv\n")
    else:
        print("\n  ✔ Реальный датасет FIFA 19 загружен.\n")

    print(f"  {loader}")           # __repr__
    print(f"  Строк: {len(loader)}")   # __len__

    # ── ЗАДАНИЕ А ─────────────────────────────────────
    print_separator("Задание А — Series и DataFrame")

    demo_a = SeriesDataFrameDemo(df)
    print(f"  {demo_a}")          # __str__ (полиморфизм)

    demo_a.show_import()
    demo_a.print_series_examples()
    demo_a.demo_loc_iloc()
    demo_a.demo_dataframe_creation()
    demo_a.print_variant_task()   # ← основное задание варианта 11

    # ── ЗАДАНИЕ Б ─────────────────────────────────────
    print_separator("Задание Б — Статистический анализ")

    analyzer = StatisticalAnalyzer(df)
    print(f"  {analyzer}")        # __str__
    print(f"  repr: {repr(analyzer)}")   # __repr__
    print(f"  'Wage' in analyzer: {'Wage' in analyzer}")  # __contains__

    analyzer.print_dataframe_info()
    analyzer.print_sprint_speed_task()
    analyzer.print_shotpower_task()

    # OOP demo
    print(f"\n  Создано анализаторов (класс. атрибут): "
          f"{StatisticalAnalyzer.get_analyzer_count()}")
    print(f"  Задача: {StatisticalAnalyzer.get_task_name()}")
