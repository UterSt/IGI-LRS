"""
matrix_ops.py — NumPy matrix analysis for Task 5 (Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Variant 11:
  a) NumPy basics: array creation, indexing, slicing, universal functions
  b) Find all elements exceeding |B|, write to array C
     Compute median of C: two ways (np.median vs. manual formula)
  c) Also demonstrate: mean, median, corrcoef, var, std on the matrix

Demonstrates OOP:
  - MatrixDisplayMixin (mixin for pretty printing)
  - BaseMatrixAnalyzer  (base class with static/dynamic attrs, magic methods)
  - MatrixAnalyzer      (concrete class, extends base, adds variant-11 logic)
"""

import numpy as np
from typing import Optional


# ─────────────────────────────────────────────
#  MIXIN
# ─────────────────────────────────────────────

class MatrixDisplayMixin:
    """Mixin that adds pretty-print helpers to a matrix class."""

    @staticmethod
    def print_matrix(matrix: np.ndarray, title: str = "Matrix") -> None:
        """
        Print a 2D numpy array in a readable grid format.

        Args:
            matrix (np.ndarray): The matrix to display.
            title  (str):        Header label.
        """
        print(f"\n  ── {title} ──")
        for row in matrix:
            print("  " + "  ".join(f"{v:6d}" for v in row))

    @staticmethod
    def print_array(arr: np.ndarray, title: str = "Array") -> None:
        """
        Print a 1D numpy array.

        Args:
            arr   (np.ndarray): The array to display.
            title (str):        Header label.
        """
        print(f"\n  ── {title} ──")
        print("  " + "  ".join(f"{v:6}" for v in arr))


# ─────────────────────────────────────────────
#  BASE ANALYSER
# ─────────────────────────────────────────────

class BaseMatrixAnalyzer(MatrixDisplayMixin):
    """
    Base class for matrix analysers.

    Demonstrates:
      - Static attributes (_DEFAULT_N, _DEFAULT_M, _DEFAULT_RANGE)
      - Dynamic attributes (_matrix, _n, _m)
      - Magic methods (__len__, __str__, __repr__)
      - Properties (matrix, shape)
    """

    _DEFAULT_N:     int   = 5      # static attributes
    _DEFAULT_M:     int   = 5
    _DEFAULT_RANGE: tuple = (-20, 21)

    def __init__(self, n: int = 0, m: int = 0, seed: Optional[int] = None):
        """
        Generate a random integer matrix A[n, m].

        Args:
            n    (int):           Number of rows.
            m    (int):           Number of columns.
            seed (int, optional): RNG seed for reproducibility.
        """
        self._n: int = n or self._DEFAULT_N
        self._m: int = m or self._DEFAULT_M

        rng = np.random.default_rng(seed)
        low, high = self._DEFAULT_RANGE
        self._matrix: np.ndarray = rng.integers(low, high, size=(self._n, self._m))

    # ── properties ─────────────────────────────────────

    @property
    def matrix(self) -> np.ndarray:
        """Read-only view of the matrix."""
        return self._matrix.copy()

    @property
    def shape(self) -> tuple:
        """Matrix shape (rows, cols)."""
        return self._matrix.shape

    # ── magic methods ──────────────────────────────────

    def __len__(self) -> int:
        """Total number of elements in the matrix."""
        return self._matrix.size

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(shape={self.shape}, size={len(self)})"

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}"
                f"(n={self._n}, m={self._m})")

    def __getitem__(self, key):
        """Allow direct indexing into the matrix: analyzer[i, j]."""
        return self._matrix[key]


# ─────────────────────────────────────────────
#  CONCRETE ANALYSER (Variant 11)
# ─────────────────────────────────────────────

class MatrixAnalyzer(BaseMatrixAnalyzer):
    """
    Full matrix analyser with NumPy statistics and Variant 11 specific logic.

    Extends BaseMatrixAnalyzer using super().
    """

    def __init__(self, n: int = 5, m: int = 5, seed: Optional[int] = None):
        """
        Initialise with a random integer matrix.

        Args:
            n    (int):           Rows.
            m    (int):           Columns.
            seed (int, optional): RNG seed.
        """
        super().__init__(n, m, seed)          # super() → BaseMatrixAnalyzer
        self._array_c: Optional[np.ndarray] = None   # dynamic attribute

    # ── property ───────────────────────────────────────

    @property
    def array_c(self) -> Optional[np.ndarray]:
        """Array C built by find_exceeding_abs; None until computed."""
        return self._array_c

    # ═══════════════════════════════════════════════════
    #  PART (a) — NumPy Basics Demo
    # ═══════════════════════════════════════════════════

    def demo_numpy_basics(self) -> None:
        """
        Demonstrate NumPy array creation, indexing, slicing, and
        universal (element-wise) functions.
        """
        print("\n  ── (а) Основы NumPy ──")

        print("\n  1. Создание массивов с np.array() и np.arange():")
        arr1 = np.array([1, 2, 3, 4, 5])
        arr2 = np.arange(1, 11, 2)
        print(f"     np.array([1..5])       : {arr1}")
        print(f"     np.arange(1,11,2)      : {arr2}")
        print(f"     матрица (первые 8 эл.) : {self._matrix.flatten()[:8]} ...")

        print("\n  2. Создание массивов заданного вида:")
        zeros = np.zeros((2, 3), dtype=int)
        ones  = np.ones((2, 3),  dtype=int)
        eye   = np.eye(3, dtype=int)
        print(f"     np.zeros(2x3) =\n{zeros}")
        print(f"     np.ones(2x3)  =\n{ones}")
        print(f"     np.eye(3)     =\n{eye}")

        print("\n  3. Индексирование и срезы матрицы:")
        print(f"     matrix[0, 0]     = {self._matrix[0, 0]}")
        print(f"     matrix[0, :]     = {self._matrix[0, :]}")
        print(f"     matrix[:, 0]     = {self._matrix[:, 0]}")
        print(f"     matrix[1:3, 1:3] =\n{self._matrix[1:3, 1:3]}")

        print("\n  4. Универсальные (поэлементные) функции:")
        print(f"     np.abs(matrix[0])    : {np.abs(self._matrix[0])}")
        print(f"     np.square(matrix[0]) : {np.square(self._matrix[0])}")
        print(f"     np.sum(matrix)       : {np.sum(self._matrix)}")
        print(f"     np.prod(matrix[0])   : {np.prod(self._matrix[0])}")
        print(f"     np.cumsum(matrix[0]) : {np.cumsum(self._matrix[0])}")

    # ═══════════════════════════════════════════════════
    #  PART (b) — Statistical Operations
    # ═══════════════════════════════════════════════════

    def demo_statistics(self) -> None:
        """
        Demonstrate NumPy statistical functions:
        mean, median, corrcoef, var, std.
        """
        m = self._matrix
        print("\n  ── (б) Математические и статистические операции ──")
        print(f"\n  np.mean(matrix)   = {np.mean(m):.4f}")
        print(f"  np.median(matrix) = {np.median(m):.4f}")
        print(f"  np.var(matrix)    = {np.var(m):.4f}")
        print(f"  np.std(matrix)    = {np.std(m):.4f}")

        if self._n >= 2:
            row1 = m[0].astype(float)
            row2 = m[-1].astype(float)
            cc = np.corrcoef(row1, row2)
            print(f"\n  np.corrcoef(строка[0], строка[-1]) =")
            print(f"    {cc[0, 1]:.6f}  (внедиагональный элемент)")

        print(f"\n  Среднее по строкам   : {np.mean(m, axis=1)}")
        print(f"  Среднее по столбцам  : {np.mean(m, axis=0)}")

    # ═══════════════════════════════════════════════════
    #  VARIANT 11 — Find elements exceeding |B|
    # ═══════════════════════════════════════════════════

    def find_exceeding_abs(self, b: float) -> np.ndarray:
        """
        Find all elements whose absolute value exceeds |B|,
        count them, and store in self._array_c.

        Args:
            b (float): Threshold value.

        Returns:
            np.ndarray: 1-D array C of elements satisfying |element| > |B|.
        """
        mask = np.abs(self._matrix) > abs(b)
        self._array_c = self._matrix[mask]
        return self._array_c

    # ── median: method 1 — np.median ───────────────────

    def median_numpy(self, arr: np.ndarray) -> float:
        """
        Compute median using np.median (standard function).

        Args:
            arr (np.ndarray): Input 1-D array.

        Returns:
            float: Median value.
        """
        return float(np.median(arr))

    # ── median: method 2 — manual formula ──────────────

    @staticmethod
    def median_manual(arr: np.ndarray) -> float:
        """
        Compute median manually by sorting and picking the middle value(s).

        If n is odd  → middle element.
        If n is even → average of the two middle elements.

        Args:
            arr (np.ndarray): Input 1-D array.

        Returns:
            float: Median value.

        Raises:
            ValueError: If array is empty.
        """
        if arr.size == 0:
            raise ValueError("Cannot compute median of an empty array.")
        sorted_arr = np.sort(arr)
        n = len(sorted_arr)
        mid = n // 2
        if n % 2 == 1:
            return float(sorted_arr[mid])
        else:
            return float((sorted_arr[mid - 1] + sorted_arr[mid]) / 2.0)

    def run_variant11(self, b: float) -> None:
        """
        Execute Variant 11 analysis: find elements exceeding |B|,
        compute median of C in two ways, and show results.

        Args:
            b (float): Threshold for absolute value comparison.
        """
        print(f"\n  ── Вариант 11: элементы с |элемент| > |{b}| ──")

        c = self.find_exceeding_abs(b)
        print(f"\n  Пороговое значение B : {b}")
        print(f"  |B|                  : {abs(b)}")
        print(f"  Найдено элементов    : {len(c)}")
        self.print_array(c, "Массив C")

        if c.size == 0:
            print("  [!] Массив C пуст — выберите меньшее значение B.")
            return

        med_np     = self.median_numpy(c)
        med_manual = self.median_manual(c)

        print(f"\n  Медиана C (np.median)    : {med_np:.6f}")
        print(f"  Медиана C (по формуле)   : {med_manual:.6f}")
        print(f"  Результаты совпадают     : {abs(med_np - med_manual) < 1e-9}")

        print(f"\n  Среднее C  : {np.mean(c):.4f}")
        print(f"  СКО C      : {np.std(c):.4f}")
        print(f"  Дисперсия C: {np.var(c):.4f}")
