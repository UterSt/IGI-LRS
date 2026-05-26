"""
series_class.py — OOP wrapper for the ln((x+1)/(x-1)) power series (Task 3).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Extends LR3 Task 1:  ln((x+1)/(x-1)) = 2·Σ 1/((2n+1)·x^(2n+1)),  |x| > 1
"""

import math
from dataclasses import dataclass, field


# ─────────────────────────────────────────────
#  DATA CONTAINER
# ─────────────────────────────────────────────

@dataclass
class SeriesResult:
    """Stores a single series computation result."""
    x:        float
    eps:      float
    fx:       float
    math_fx:  float
    n_terms:  int
    error:    float = field(init=False)

    def __post_init__(self):
        self.error = abs(self.fx - self.math_fx)

    def __str__(self) -> str:
        return (f"x={self.x:.4f}  n={self.n_terms:>4}  "
                f"F(x)={self.fx:.8f}  Math={self.math_fx:.8f}  "
                f"err={self.error:.2e}")


# ─────────────────────────────────────────────
#  BASE SERIES CLASS
# ─────────────────────────────────────────────

class BaseSeries:
    """
    Abstract base for series computations.

    Demonstrates:
      - Static attributes (MAX_ITER)
      - Abstract-style method compute() — raises NotImplementedError
      - Magic methods (__len__, __repr__)
    """

    MAX_ITER: int = 500    # static attribute

    def __init__(self):
        self._results: list[SeriesResult] = []   # dynamic attribute

    def compute(self, x: float, eps: float) -> SeriesResult:
        """Subclasses must override this method."""
        raise NotImplementedError("Subclasses must implement compute().")

    def __len__(self) -> int:
        return len(self._results)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(results={len(self._results)})"

    def __iter__(self):
        return iter(self._results)

    @property
    def results(self) -> list[SeriesResult]:
        """All stored computation results."""
        return list(self._results)


# ─────────────────────────────────────────────
#  CONCRETE SERIES — ln((x+1)/(x-1))
# ─────────────────────────────────────────────

class LnRatioSeries(BaseSeries):
    """
    Computes ln((x+1)/(x-1)) by the power series:

        2 · Σ_{n=0}^∞  1 / ((2n+1) · x^(2n+1)),   |x| > 1

    Inherits BaseSeries. Uses super() in __init__.
    """

    _series_name: str = "ln((x+1)/(x-1))"  # static attribute

    def __init__(self):
        super().__init__()                          # super() call

    # ── class method ───────────────────────────────────

    @classmethod
    def get_series_name(cls) -> str:
        """
        Return the human-readable name of this series.

        Returns:
            str: Series name.
        """
        return cls._series_name

    # ── static method ──────────────────────────────────

    @staticmethod
    def math_reference(x: float) -> float:
        """
        Compute the exact value using math.log.

        Args:
            x (float): Argument (|x| > 1).

        Returns:
            float: Exact value of ln((x+1)/(x-1)).
        """
        return math.log((x + 1) / (x - 1))

    # ── override ───────────────────────────────────────

    def compute(self, x: float, eps: float) -> SeriesResult:
        """
        Compute the series approximation for a single x and eps.

        Args:
            x   (float): Argument; |x| must be > 1.
            eps (float): Desired precision; must be > 0.

        Returns:
            SeriesResult: Full result including error.

        Raises:
            ValueError: If constraints on x or eps are violated.
        """
        if abs(x) <= 1:
            raise ValueError(f"|x| must be > 1, got x={x}")
        if eps <= 0:
            raise ValueError(f"eps must be > 0, got eps={eps}")

        total   = 0.0
        n_terms = 0

        for n in range(self.MAX_ITER):
            power = 2 * n + 1
            term  = 1.0 / (power * (x ** power))
            total += term
            n_terms += 1
            if abs(term) < eps:
                break

        fx      = 2 * total
        math_fx = self.math_reference(x)
        result  = SeriesResult(x=x, eps=eps, fx=fx, math_fx=math_fx, n_terms=n_terms)
        self._results.append(result)
        return result

    def compute_range(self, x_values: list[float], eps: float) -> list[SeriesResult]:
        """
        Compute the series for a list of x values.

        Args:
            x_values (list[float]): List of x values (each must satisfy |x|>1).
            eps      (float):       Precision.

        Returns:
            list[SeriesResult]: One result per valid x value.
        """
        results = []
        for x in x_values:
            try:
                results.append(self.compute(x, eps))
            except ValueError:
                pass   # skip invalid x values silently
        return results

    # ── display ────────────────────────────────────────

    def print_table(self) -> None:
        """Print all stored results in a formatted table."""
        if not self._results:
            print("  Нет результатов для отображения.")
            return
        col = 14
        print()
        print("  " + "─" * (col * 5 + 2))
        print(f"  {'x':^{col}}{'n':^{col}}{'F(x)':^{col}}{'Math F(x)':^{col}}{'eps':^{col}}")
        print("  " + "─" * (col * 5 + 2))
        for r in self._results:
            print(f"  {r.x:^{col}.6f}{r.n_terms:^{col}}{r.fx:^{col}.8f}"
                  f"{r.math_fx:^{col}.8f}{r.eps:^{col}}")
        print("  " + "─" * (col * 5 + 2))

    def __str__(self) -> str:
        return f"LnRatioSeries | {len(self._results)} computed point(s)"
