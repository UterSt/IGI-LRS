# =============================================================================
# Lab Work #3: Standard Data Types, Collections, Functions, Modules
# File: task3_strings.py — Count uppercase English vowels in a string.
#                          No regular expressions used.
# Version: 1.0
# Developer: Student, Variant 11
# Date: 2025
# =============================================================================

from utils import print_separator

# All uppercase English vowels
UPPERCASE_VOWELS = frozenset("AEIOU")


# ─────────────────────────────────────────────
#  INPUT
# ─────────────────────────────────────────────

def read_string():
    """
    Prompt the user to enter a non-empty string.
    Repeats until at least one character is provided.

    Returns:
        str: A non-empty string entered by the user.
    """
    while True:
        text = input("  Введите строку: ")
        if text:
            return text
        print("  [ошибка] Строка не может быть пустой. Попробуйте снова.")


# ─────────────────────────────────────────────
#  CORE COMPUTATION
# ─────────────────────────────────────────────

def count_uppercase_vowels(text):
    """
    Count the number of uppercase English vowel letters (A, E, I, O, U)
    in the given string. No regular expressions are used.

    Args:
        text (str): The input string to analyse.

    Returns:
        int: The count of uppercase English vowels found.
    """
    count = 0
    for char in text:
        if char in UPPERCASE_VOWELS:
            count += 1
    return count


def find_uppercase_vowels(text):
    """
    Collect all uppercase English vowels found in the string,
    preserving their order of appearance.

    Args:
        text (str): The input string to analyse.

    Returns:
        list[str]: An ordered list of found uppercase vowel characters.
    """
    found = []
    for char in text:
        if char in UPPERCASE_VOWELS:
            found.append(char)
    return found


# ─────────────────────────────────────────────
#  OUTPUT
# ─────────────────────────────────────────────

def print_result(text, count, found):
    """
    Display the analysis results: original string, found vowels, and count.

    Args:
        text  (str):      The original input string.
        count (int):      Total number of uppercase vowels found.
        found (list[str]): The list of uppercase vowels in order.
    """
    print()
    print(f"  Входная строка   : {text}")
    print(f"  Ищем гласные     : {', '.join(sorted(UPPERCASE_VOWELS))}")
    print()

    if found:
        print(f"  Найденные буквы  : {', '.join(found)}")
    else:
        print("  Найденные буквы  : — нет —")

    print(f"  Итого найдено    : {count}")


# ─────────────────────────────────────────────
#  MAIN TASK ENTRY POINT
# ─────────────────────────────────────────────

def run_task3():
    """
    Main entry point for Task 3.
    Reads a string from the user, counts and displays the number of
    uppercase English vowel letters (A, E, I, O, U). No regex used.
    """
    print_separator("Задание 3 — Подсчёт заглавных гласных английских букв")
    print("  Подсчитываются буквы: A, E, I, O, U  (только заглавные)\n")

    try:
        text  = read_string()
        count = count_uppercase_vowels(text)
        found = find_uppercase_vowels(text)
        print_result(text, count, found)
    except Exception as e:
        print(f"  [ошибка] Непредвиденная ошибка: {e}")
