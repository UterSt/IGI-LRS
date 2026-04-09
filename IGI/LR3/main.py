# =============================================================================
# Lab Work #3: Standard Data Types, Collections, Functions, Modules
# File: main.py — Main module: interactive menu, launches all tasks.
# Version: 1.0
# Developer: Student, Variant 11
# Date: 2025
# =============================================================================

from utils         import run_with_repeat, print_separator
from task1_series  import run_task1
from task2_sequence import run_task2
from task3_strings import run_task3
from task4_text    import run_task4
from task5_lists   import run_task5


# ─────────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────────

MENU_ITEMS = {
    "1": ("Степенной ряд  — ln((x+1)/(x-1))",           run_task1),
    "2": ("Цикл с минимумом — конец ввода: 0",           run_task2),
    "3": ("Анализ строки — заглавные гласные",           run_task3),
    "4": ("Анализ текста — строка про Белого Кролика",   run_task4),
    "5": ("Обработка списка — диапазон и сумма",         run_task5),
    "0": ("Выход",                                        None),
}


def print_menu():
    """
    Display the main interactive menu with all available tasks.
    """
    print_separator("Лабораторная работа №3  —  Вариант 11")
    print("  Выберите задание:\n")
    for key, (label, _) in MENU_ITEMS.items():
        prefix = "  [0]  " if key == "0" else f"  [{key}]  "
        print(f"{prefix}{label}")
    print()


def get_menu_choice():
    """
    Prompt the user to select a menu item.
    Repeats until a valid key is entered.

    Returns:
        str: The valid menu key chosen by the user.
    """
    valid_keys = set(MENU_ITEMS.keys())
    while True:
        choice = input("  Ваш выбор: ").strip()
        if choice in valid_keys:
            return choice
        print(f"  [ошибка] Введите одно из: {', '.join(sorted(valid_keys))}")


# ─────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────

def main():
    """
    Main program loop.
    Shows the menu, runs the selected task with repeat support,
    and exits cleanly when the user chooses 0.
    """
    print("\n" + "=" * 60)
    print("  Добро пожаловать в Лабораторную работу №3")
    print("  Тема: Типы данных, коллекции, функции, модули")
    print("  Разработчик: Студент, Вариант 11")
    print("=" * 60)

    while True:
        print_menu()
        choice = get_menu_choice()

        if choice == "0":
            print("\n  До свидания! Выход из программы.\n")
            break

        label, task_func = MENU_ITEMS[choice]
        run_with_repeat(task_func)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n  [инфо] Программа прервана пользователем (Ctrl+C). До свидания!")
