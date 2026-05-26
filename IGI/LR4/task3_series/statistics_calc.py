"""
statistics_calc.py — Statistical analysis class for Task 3.
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Computes: mean, median, mode, variance (population), standard deviation.
All formulas implemented manually (no statistics module).
"""

from collections import Counter


# ─────────────────────────────────────────────
#  STATISTICS CLASS
# ─────────────────────────────────────────────

class Statistics:
    """
    Computes descriptive statistics for a sequence of numbers.

    Demonstrates:
      - Static attributes (_ROUND_DIGITS)
      - Dynamic attributes (_data, _n)
      - Properties (mean, median, mode, variance, std)
      - Magic methods (__len__, __str__, __repr__)
      - Cached computation via private method
    """

    _ROUND_DIGITS: int = 6    # static attribute — precision for display

    def __init__(self, data: list[float]):
        """
        Initialise with a list of numeric values.

        Args:
            data (list[float]): The sequence to analyse.

        Raises:
            ValueError: If the data list is empty.
        """
        if not data:
            raise ValueError("Data must not be empty.")
        self._data: list[float] = list(data)    # dynamic attribute — copy
        self._n:    int         = len(self._data)
        self._cache: dict       = {}             # dynamic attribute — lazy cache

    # ── properties ─────────────────────────────────────

    @property
    def data(self) -> list[float]:
        """Read-only copy of the data."""
        return list(self._data)

    @property
    def n(self) -> int:
        """Number of data points."""
        return self._n

    @property
    def mean(self) -> float:
        """
        Arithmetic mean (average).

        Returns:
            float: Mean value.
        """
        if "mean" not in self._cache:
            self._cache["mean"] = sum(self._data) / self._n
        return self._cache["mean"]

    @property
    def median(self) -> float:
        """
        Median (middle value of sorted data).

        Returns:
            float: Median value.
        """
        if "median" not in self._cache:
            sorted_data = sorted(self._data)
            mid = self._n // 2
            if self._n % 2 == 1:
                self._cache["median"] = float(sorted_data[mid])
            else:
                self._cache["median"] = (sorted_data[mid - 1] + sorted_data[mid]) / 2.0
        return self._cache["median"]

    @property
    def mode(self):
        """
        Mode (most frequent value). Returns list if multiple modes exist.

        Returns:
            float | list[float]: The mode(s).
        """
        if "mode" not in self._cache:
            counts  = Counter(self._data)
            max_cnt = max(counts.values())
            modes   = [v for v, c in counts.items() if c == max_cnt]
            self._cache["mode"] = modes[0] if len(modes) == 1 else modes
        return self._cache["mode"]

    @property
    def variance(self) -> float:
        """
        Population variance: Σ(xᵢ − μ)² / n.

        Returns:
            float: Variance.
        """
        if "variance" not in self._cache:
            mu = self.mean
            self._cache["variance"] = sum((x - mu) ** 2 for x in self._data) / self._n
        return self._cache["variance"]

    @property
    def std(self) -> float:
        """
        Population standard deviation: √variance.

        Returns:
            float: Standard deviation.
        """
        if "std" not in self._cache:
            self._cache["std"] = self.variance ** 0.5
        return self._cache["std"]

    # ── display ────────────────────────────────────────

    def print_summary(self, title: str = "Statistics") -> None:
        """
        Print a formatted statistics summary.

        Args:
            title (str): Optional section title.
        """
        r = self._ROUND_DIGITS
        mode_str = (str([round(m, r) for m in self.mode])
                    if isinstance(self.mode, list)
                    else str(round(self.mode, r)))

        print(f"\n  ── {title} (n={self._n}) ──")
        print(f"  Среднее арифм.: {round(self.mean,     r)}")
        print(f"  Медиана       : {round(self.median,   r)}")
        print(f"  Мода          : {mode_str}")
        print(f"  Дисперсия     : {round(self.variance, r)}")
        print(f"  СКО           : {round(self.std,      r)}")

    # ── magic methods ──────────────────────────────────

    def __len__(self) -> int:
        return self._n

    def __str__(self) -> str:
        r = self._ROUND_DIGITS
        return (f"Statistics(n={self._n}, mean={round(self.mean,r)}, "
                f"std={round(self.std,r)})")

    def __repr__(self) -> str:
        return f"Statistics(data={self._data[:5]}{'...' if self._n > 5 else ''})"
