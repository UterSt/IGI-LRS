from utils import input_float, print_separator
from initializers import choose_initialization, display_list


# ─────────────────────────────────────────────
#  INPUT — range boundaries
# ─────────────────────────────────────────────

def get_range():
    """
    Prompt the user to enter the range boundaries A and B.
    Ensures A <= B, asking again if the condition is violated.

    Returns:
        tuple[float, float]: (A, B) where A <= B.
    """
    print("  Введите границы диапазона [A, B]:")
    while True:
        a = input_float("    A: ")
        b = input_float("    B: ")
        if a <= b:
            return a, b
        print("  [ошибка] A должно быть меньше или равно B. Попробуйте снова.")


# ─────────────────────────────────────────────
#  SUBTASK A — count elements in [A, B]
# ─────────────────────────────────────────────

def count_in_range(numbers, a, b):
    """
    Count how many elements of the list fall within the closed range [A, B].

    Args:
        numbers (list[float]): The source list.
        a       (float):       Lower boundary (inclusive).
        b       (float):       Upper boundary (inclusive).

    Returns:
        int: Number of elements satisfying A <= element <= B.
    """
    count = 0
    for num in numbers:
        if a <= num <= b:
            count += 1
    return count


def get_elements_in_range(numbers, a, b):
    """
    Collect all elements from the list that fall within [A, B].

    Args:
        numbers (list[float]): The source list.
        a       (float):       Lower boundary (inclusive).
        b       (float):       Upper boundary (inclusive).

    Returns:
        list[float]: Elements satisfying A <= element <= B.
    """
    result = []
    for num in numbers:
        if a <= num <= b:
            result.append(num)
    return result


# ─────────────────────────────────────────────
#  SUBTASK B — sum of elements after the maximum
# ─────────────────────────────────────────────

def find_max_index(numbers):
    """
    Find the index of the maximum element in the list.
    If several elements share the maximum value, the first occurrence
    is returned.

    Args:
        numbers (list[float]): The source list (must be non-empty).

    Returns:
        int: 0-based index of the maximum element.
    """
    max_idx = 0
    for i in range(1, len(numbers)):
        if numbers[i] > numbers[max_idx]:
            max_idx = i
    return max_idx


def sum_after_maximum(numbers):
    """
    Compute the sum of all elements that come after the maximum element.

    Args:
        numbers (list[float]): The source list (must be non-empty).

    Returns:
        tuple[float, int, int]:
            (total_sum, max_index, count_after) where
            total_sum   — sum of elements after the maximum,
            max_index   — 0-based index of the maximum element,
            count_after — number of elements summed.

    Raises:
        ValueError: If the list is empty.
    """
    if not numbers:
        raise ValueError("Cannot process an empty list.")

    max_idx     = find_max_index(numbers)
    tail        = numbers[max_idx + 1:]   # elements after the maximum
    total_sum   = sum(tail)
    return total_sum, max_idx, len(tail)


# ─────────────────────────────────────────────
#  OUTPUT
# ─────────────────────────────────────────────

def print_range_result(a, b, count, elements):
    """
    Display the result of the range-count subtask.

    Args:
        a        (float):       Lower boundary.
        b        (float):       Upper boundary.
        count    (int):         Number of elements in range.
        elements (list[float]): The elements found in range.
    """
    print(f"\n  ── а) Элементы в диапазоне [{a}, {b}] ─────────────")
    if elements:
        formatted = ",  ".join(f"{v:.2f}" for v in elements)
        print(f"  Элементы  : {formatted}")
    else:
        print("  Элементы  : — нет —")
    print(f"  Количество: {count}")


def print_sum_result(numbers, max_idx, total_sum, count_after):
    """
    Display the result of the sum-after-maximum subtask.

    Args:
        numbers     (list[float]): The full list.
        max_idx     (int):         0-based index of the maximum.
        total_sum   (float):       Sum of elements after the maximum.
        count_after (int):         Number of elements summed.
    """
    print(f"\n  ── б) Сумма элементов после максимального ─────────")
    print(f"  Максимум      : {numbers[max_idx]:.2f}  (позиция № {max_idx + 1})")

    if count_after == 0:
        print("  После максимума элементов нет — он последний.")
        print(f"  Сумма         : 0.00")
    else:
        tail_str = ",  ".join(f"{v:.2f}" for v in numbers[max_idx + 1:])
        print(f"  Элементы после: {tail_str}")
        print(f"  Количество    : {count_after}")
        print(f"  Сумма         : {total_sum:.2f}")


# ─────────────────────────────────────────────
#  MAIN TASK ENTRY POINT
# ─────────────────────────────────────────────

def run_task5():
    """
    Main entry point for Task 5.
    Initialises a list of float numbers (via generator or user input),
    then:
      a) counts elements in a user-defined range [A, B],
      b) computes the sum of elements after the maximum element.
    """
    print_separator("Задание 5 — Обработка вещественного списка")

    numbers = []

    try:
        # Initialise the list using the shared initializers module
        choose_initialization(numbers)

        if not numbers:
            print("  [инфо] Список пуст. Нечего обрабатывать.")
            return

        # Display the initialised list
        display_list(numbers)

        # ── Subtask a) ───────────────────────────────
        print()
        a, b     = get_range()
        count    = count_in_range(numbers, a, b)
        elements = get_elements_in_range(numbers, a, b)
        print_range_result(a, b, count, elements)

        # ── Subtask b) ───────────────────────────────
        total_sum, max_idx, count_after = sum_after_maximum(numbers)
        print_sum_result(numbers, max_idx, total_sum, count_after)

    except ValueError as e:
        print(f"  [ошибка] Ошибка значения: {e}")
    except Exception as e:
        print(f"  [ошибка] Непредвиденная ошибка: {e}")
