# =============================================================================
# Lab Work #3: Standard Data Types, Collections, Functions, Modules
# File: task2_sequence.py — Find the minimum of entered integers. Stop on 0.
# Version: 1.0
# Developer: Student, Variant 11
# Date: 2025
# =============================================================================

from utils import print_separator


# ─────────────────────────────────────────────
#  INPUT
# ─────────────────────────────────────────────

def read_integer(prompt):
    """
    Prompt the user to enter an integer value.
    Repeats until a valid integer is provided.

    Args:
        prompt (str): Message shown to the user.

    Returns:
        int: The validated integer value.
    """
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("  [ошибка] Введите целое число (например: -5, 0, 42).")


# ─────────────────────────────────────────────
#  CORE COMPUTATION
# ─────────────────────────────────────────────

def collect_numbers():
    """
    Collect integers from the user in a loop until 0 is entered.
    The terminator (0) is not included in the result.

    Returns:
        list[int]: A list of all entered integers (excluding the terminator 0).
    """
    numbers = []
    print("  Вводите целые числа по одному. Введите 0 для завершения.\n")

    while True:
        value = read_integer(f"  Число [{len(numbers) + 1}]: ")
        if value == 0:
            break
        numbers.append(value)

    return numbers


def find_minimum(numbers):
    """
    Find and return the minimum value in the list.

    Args:
        numbers (list[int]): A non-empty list of integers.

    Returns:
        int: The minimum value in the list.
    """
    minimum = numbers[0]
    for num in numbers[1:]:
        if num < minimum:
            minimum = num
    return minimum


# ─────────────────────────────────────────────
#  OUTPUT
# ─────────────────────────────────────────────

def print_numbers(numbers):
    """
    Display all entered numbers in a single formatted line.

    Args:
        numbers (list[int]): The list of integers to display.
    """
    formatted = ",  ".join(str(n) for n in numbers)
    print(f"\n  Введённые числа : {formatted}")
    print(f"  Количество      : {len(numbers)}")


def print_minimum(minimum):
    """
    Display the found minimum value.

    Args:
        minimum (int): The minimum value to display.
    """
    print(f"  Минимальное значение : {minimum}")


# ─────────────────────────────────────────────
#  MAIN TASK ENTRY POINT
# ─────────────────────────────────────────────

def run_task2():
    """
    Main entry point for Task 2.
    Collects integers from the user until 0 is entered,
    then finds and displays the minimum value.
    """
    print_separator("Задание 2 — Нахождение минимума (конец: 0)")

    numbers = collect_numbers()

    if not numbers:
        print("\n  [инфо] Числа не были введены (получен только 0).")
        print("  Минимум не может быть определён.")
        return

    print_numbers(numbers)

    try:
        minimum = find_minimum(numbers)
        print_minimum(minimum)
    except Exception as e:
        print(f"  [ошибка] Непредвиденная ошибка: {e}")
