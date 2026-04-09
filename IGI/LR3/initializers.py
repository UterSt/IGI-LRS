import random
from utils import input_float, input_positive_int, print_separator


# ─────────────────────────────────────────────
#  GENERATOR-BASED INITIALIZATION
# ─────────────────────────────────────────────

def _float_generator(size, low=-100.0, high=100.0):
    """
    Generator that yields random float values in the range [low, high].

    Args:
        size (int): Number of values to generate.
        low (float): Lower bound of the random range.
        high (float): Upper bound of the random range.

    Yields:
        float: A random float rounded to 2 decimal places.
    """
    for _ in range(size):
        yield round(random.uniform(low, high), 2)


def init_by_generator(sequence):
    """
    Fill the given sequence (list) with random float values using a generator.
    The size of the sequence is determined by the user.

    Args:
        sequence (list): An empty list to be filled with generated values.

    Returns:
        list: The same list filled with random float values.
    """
    print_separator("Инициализация генератором")
    size = input_positive_int("  Введите размер списка: ")
    low  = input_float("  Введите нижнюю границу (например -100): ")
    high = input_float("  Введите верхнюю границу (например  100): ")

    # Validate that low < high
    while low >= high:
        print("  [ошибка] Нижняя граница должна быть меньше верхней.")
        low  = input_float("  Введите нижнюю границу: ")
        high = input_float("  Введите верхнюю границу: ")

    sequence.clear()
    sequence.extend(_float_generator(size, low, high))

    print(f"\n  Сгенерировано {size} элементов в диапазоне [{low}, {high}].")
    return sequence


# ─────────────────────────────────────────────
#  USER-INPUT INITIALIZATION
# ─────────────────────────────────────────────

def init_by_user(sequence):
    """
    Fill the given sequence (list) with float values entered by the user.
    The size of the sequence is determined by the user.

    Args:
        sequence (list): An empty list to be filled with user-provided values.

    Returns:
        list: The same list filled with user-entered float values.
    """
    print_separator("Ручной ввод")
    size = input_positive_int("  Введите размер списка: ")

    sequence.clear()
    print(f"  Введите {size} чисел (допустимы дробные):")

    for i in range(size):
        value = input_float(f"    Элемент [{i}]: ")
        sequence.append(value)

    print(f"\n  Успешно введено {size} элементов.")
    return sequence


# ─────────────────────────────────────────────
#  DISPLAY LIST
# ─────────────────────────────────────────────

def display_list(sequence):
    """
    Print all elements of the list in a formatted, numbered view.

    Args:
        sequence (list): The list to display.
    """
    if not sequence:
        print("  [инфо] Список пуст.")
        return

    print("\n  Содержимое списка:")
    print("  " + "-" * 40)
    for i, val in enumerate(sequence):
        print(f"    [{i:>2}]  {val:>10.2f}")
    print("  " + "-" * 40)
    print(f"  Всего элементов: {len(sequence)}")


# ─────────────────────────────────────────────
#  INITIALIZATION MENU
# ─────────────────────────────────────────────

def choose_initialization(sequence):
    """
    Show a menu for the user to choose how to initialize the list:
    via random generator or manual input.

    Args:
        sequence (list): The list to initialize.

    Returns:
        list: The initialized list.
    """
    print_separator("Выбор метода инициализации")
    print("  1. Случайный генератор")
    print("  2. Ручной ввод")

    while True:
        choice = input("\n  Ваш выбор (1 или 2): ").strip()
        if choice == '1':
            return init_by_generator(sequence)
        elif choice == '2':
            return init_by_user(sequence)
        else:
            print("  [ошибка] Введите 1 или 2.")
