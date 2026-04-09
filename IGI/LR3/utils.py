# =============================================================================
# Lab Work #3: Standard Data Types, Collections, Functions, Modules
# File: utils.py — Utility functions: input validation, decorator, repeat loop
# Version: 1.0
# Developer: Student, Variant 11
# Date: 2025
# =============================================================================

import time
import functools


# ─────────────────────────────────────────────
#  DECORATOR: execution time logger
# ─────────────────────────────────────────────

def timer_decorator(func):
    """
    Decorator that measures and prints the execution time of a function.

    Args:
        func: The function to wrap.

    Returns:
        wrapper: The wrapped function with timing output.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"  [таймер] '{func.__name__}' выполнена за {elapsed:.6f} сек")
        return result
    return wrapper


# ─────────────────────────────────────────────
#  INPUT VALIDATION FUNCTIONS
# ─────────────────────────────────────────────

def input_float(prompt):
    """
    Prompt the user to enter a float value. Repeats until valid input is given.

    Args:
        prompt (str): Message shown to the user.

    Returns:
        float: The validated float value.
    """
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  [ошибка] Введите корректное число (например: 3.14).")


def input_int(prompt):
    """
    Prompt the user to enter an integer value. Repeats until valid input is given.

    Args:
        prompt (str): Message shown to the user.

    Returns:
        int: The validated integer value.
    """
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("  [ошибка] Введите целое число (например: 5).")


def input_float_constrained(prompt, condition, error_msg):
    """
    Prompt the user for a float that satisfies a given condition.

    Args:
        prompt (str): Message shown to the user.
        condition (callable): A function that takes a float and returns bool.
        error_msg (str): Message shown when the condition is not satisfied.

    Returns:
        float: The validated and constrained float value.
    """
    while True:
        value = input_float(prompt)
        if condition(value):
            return value
        print(f"  [error] {error_msg}")


def input_positive_int(prompt):
    """
    Prompt the user to enter a positive integer (>= 1).

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


# ─────────────────────────────────────────────
#  REPEAT EXECUTION WRAPPER
# ─────────────────────────────────────────────

def run_with_repeat(task_func):
    """
    Run a task function in a loop, asking the user after each run
    whether they want to repeat or return to the main menu.

    Args:
        task_func (callable): The task function to execute repeatedly.
    """
    while True:
        task_func()
        print()
        again = input("  Повторить задание? (д / н): ").strip().lower()
        if again != 'д':
            print("  Возврат в главное меню...\n")
            break


# ─────────────────────────────────────────────
#  MENU SEPARATOR HELPER
# ─────────────────────────────────────────────

def print_separator(title=""):
    """
    Print a visual separator line with an optional title.

    Args:
        title (str): Optional label shown in the center of the separator.
    """
    width = 60
    if title:
        side = (width - len(title) - 2) // 2
        print("\n" + "─" * side + f" {title} " + "─" * side)
    else:
        print("\n" + "─" * width)
