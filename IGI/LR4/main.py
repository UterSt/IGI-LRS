"""
main.py — Main entry point for Laboratory Work #4 (Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Runs all five tasks from a menu.  Each task can be repeated without
restarting the program.  Invalid input is handled at every prompt.

Usage:
    python main.py
"""

import os
import sys

# Ensure the project root is on sys.path so all modules are importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import print_separator, run_with_repeat


# ─────────────────────────────────────────────
#  LAZY IMPORTS (only load a task when chosen)
# ─────────────────────────────────────────────

def _run_task1():
    from task1_synonyms.task1_main import run_task1
    run_task1()

def _run_task2():
    from task2_regex.task2_main import run_task2
    run_task2()

def _run_task3():
    from task3_series.task3_main import run_task3
    run_task3()

def _run_task4():
    from task4_geometry.task4_main import run_task4
    run_task4()

def _run_task5():
    from task5_numpy.task5_main import run_task5
    run_task5()

def _run_task6():
    from task6_pandas.task6_main import run_task6
    run_task6()


TASKS = {
    "1": ("Словарь синонимов  (CSV + Pickle)",      _run_task1),
    "2": ("Анализ текста (regex)",                   _run_task2),
    "3": ("Ряды + Статистика + График",              _run_task3),
    "4": ("Геометрические фигуры (matplotlib)",      _run_task4),
    "5": ("Анализ матриц (NumPy)",                   _run_task5),
    "6": ("Pandas — FIFA 19 (Вариант 11)",            _run_task6),
}


# ─────────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────────

def print_menu() -> None:
    """Print the main task selection menu."""
    print_separator("ЛР4 — Вариант 11  |  Главное меню")
    for key, (title, _) in TASKS.items():
        print(f"  [{key}]  Задание {key}: {title}")
    print("  [0]  Выход")
    print()


def get_choice() -> str:
    """
    Read and validate the user's menu choice.

    Returns:
        str: A valid key from TASKS, or '0' to exit.
    """
    valid = set(TASKS.keys()) | {"0"}
    while True:
        raw = input("  Your choice: ").strip()
        if raw in valid:
            return raw
        print(f"  [ошибка] Введите одно из: {sorted(valid)}")


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

def main() -> None:
    """
    Main loop: show menu, dispatch to chosen task, allow repetition.
    """
    print("\n" + "=" * 64)
    print("   Лабораторная работа №4  —  Python")
    print("   Тема: Файлы, Классы, Сериализаторы, Regex, NumPy")
    print("   Вариант: 11")
    print("=" * 64)

    while True:
        print_menu()
        choice = get_choice()

        if choice == "0":
            print("\n  До свидания!\n")
            break

        title, func = TASKS[choice]
        run_with_repeat(func)


if __name__ == "__main__":
    main()
