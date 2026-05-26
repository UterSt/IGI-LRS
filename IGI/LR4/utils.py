"""
utils.py — Shared utility functions for Laboratory Work #4.
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11
"""

import time
import functools
import os


# ─────────────────────────────────────────────
#  DECORATOR: execution-time logger
# ─────────────────────────────────────────────

def timer_decorator(func):
    """
    Decorator that measures and prints execution time of a function.

    Args:
        func: The function to wrap.

    Returns:
        wrapper: The wrapped function with timing output.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start  = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  [таймер] '{func.__name__}' выполнена за {elapsed:.6f} с")
        return result
    return wrapper


# ─────────────────────────────────────────────
#  INPUT VALIDATION
# ─────────────────────────────────────────────

def input_float(prompt: str) -> float:
    """
    Prompt the user for a float. Loops until valid input is given.

    Args:
        prompt (str): Message shown to the user.

    Returns:
        float: The validated float value.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  [ошибка] Введите корректное число (например 3.14).")


def input_int(prompt: str) -> int:
    """
    Prompt the user for an integer. Loops until valid input is given.

    Args:
        prompt (str): Message shown to the user.

    Returns:
        int: The validated integer value.
    """
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("  [ошибка] Введите целое число (например 5).")


def input_float_constrained(prompt: str, condition, error_msg: str) -> float:
    """
    Prompt for a float that satisfies a given condition.

    Args:
        prompt     (str):      Message shown to the user.
        condition  (callable): Function(float) -> bool.
        error_msg  (str):      Message shown when condition fails.

    Returns:
        float: A valid float satisfying the condition.
    """
    while True:
        value = input_float(prompt)
        if condition(value):
            return value
        print(f"  [ошибка] {error_msg}")


def input_positive_int(prompt: str) -> int:
    """
    Prompt for a positive integer (>= 1).

    Args:
        prompt (str): Message shown to the user.

    Returns:
        int: A positive integer.
    """
    while True:
        value = input_int(prompt)
        if value >= 1:
            return value
        print("  [ошибка] Введите положительное целое число (>= 1).")


def input_positive_float(prompt: str) -> float:
    """
    Prompt for a positive float (> 0).

    Args:
        prompt (str): Message shown to the user.

    Returns:
        float: A positive float.
    """
    return input_float_constrained(prompt, lambda v: v > 0, "Значение должно быть положительным.")


def input_string_nonempty(prompt: str) -> str:
    """
    Prompt the user for a non-empty string.

    Args:
        prompt (str): Message shown to the user.

    Returns:
        str: A non-empty stripped string.
    """
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("  [ошибка] Ввод не может быть пустым.")


# ─────────────────────────────────────────────
#  REPEAT / MENU HELPERS
# ─────────────────────────────────────────────

def run_with_repeat(task_func):
    """
    Run a task in a loop, asking after each run whether to repeat.

    Args:
        task_func (callable): The task function to execute.
    """
    while True:
        task_func()
        print()
        again = input("  Повторить задание? (д / н): ").strip().lower()
        if again not in ('д', 'y', 'да'):
            print("  Возврат в главное меню...\n")
            break


def print_separator(title: str = ""):
    """
    Print a visual separator line with an optional centered title.

    Args:
        title (str): Optional label shown in the separator.
    """
    width = 64
    if title:
        side = (width - len(title) - 2) // 2
        print("\n" + "─" * side + f" {title} " + "─" * side)
    else:
        print("\n" + "─" * width)


def ensure_dir(path: str):
    """
    Create a directory if it does not already exist.

    Args:
        path (str): Directory path to create.
    """
    os.makedirs(path, exist_ok=True)
