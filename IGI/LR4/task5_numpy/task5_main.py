"""
task5_main.py — Entry point for Task 5: NumPy Matrix Analysis (Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Variant 11:
  - Find all elements exceeding |B| by absolute value, store in array C
  - Compute median of C: via np.median AND via manual formula
"""

from utils import (print_separator, input_positive_int, input_int,
                   input_float)
from task5_numpy.matrix_ops import MatrixAnalyzer


# ─────────────────────────────────────────────
#  INPUT
# ─────────────────────────────────────────────

def get_matrix_size() -> tuple[int, int]:
    """
    Prompt the user for matrix dimensions n and m.

    Returns:
        tuple[int, int]: (n rows, m columns).
    """
    n = input_positive_int("  Введите количество строк    n (>= 1): ")
    m = input_positive_int("  Введите количество столбцов m (>= 1): ")
    return n, m


def get_threshold() -> float:
    """
    Prompt the user for the threshold value B.

    Returns:
        float: The threshold B.
    """
    return input_float("  Введите пороговое значение B (любое число): ")


# ─────────────────────────────────────────────
#  MAIN TASK ENTRY POINT
# ─────────────────────────────────────────────

def run_task5() -> None:
    """
    Main entry point for Task 5 — NumPy Matrix Analysis.

    Generates a random integer matrix, demonstrates NumPy basics,
    statistical operations, and performs Variant 11 specific analysis.
    """
    print_separator("Задание 5 — Анализ матриц NumPy (Вариант 11)")

    print("  Генерация случайной целочисленной матрицы A[n, m]")
    n, m = get_matrix_size()
    seed = 42

    analyzer = MatrixAnalyzer(n, m, seed=seed)

    print(f"\n  {analyzer}")
    print(f"  repr : {repr(analyzer)}")
    print(f"  len  : {len(analyzer)} элементов")
    print(f"  shape: {analyzer.shape}")

    analyzer.print_matrix(analyzer.matrix, "Сгенерированная матрица A")

    analyzer.demo_numpy_basics()
    analyzer.demo_statistics()

    print()
    b = get_threshold()
    analyzer.run_variant11(b)
