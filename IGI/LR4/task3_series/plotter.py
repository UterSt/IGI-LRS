"""
plotter.py — Matplotlib plotting for the ln series (Task 3).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Plots:
  - Series approximation F(x) from computed results
  - Exact reference Math F(x) computed with math.log
  - Coordinate axes, legend, annotation, title
"""

import math
import os
import matplotlib.pyplot as plt
import numpy as np


# ─────────────────────────────────────────────
#  PLOTTER CLASS
# ─────────────────────────────────────────────

class SeriesPlotter:
    """
    Creates and saves comparison plots for the power series vs. math function.

    Demonstrates:
      - Static attributes (DEFAULT_OUTPUT, FIGURE_SIZE, DPI)
      - Dynamic attributes (_fig, _ax, _output_path)
      - Properties with setters
      - Magic methods (__repr__)
    """

    DEFAULT_OUTPUT: str   = "output/task3_series_plot.png"   # static
    FIGURE_SIZE:    tuple = (11, 6)                           # static
    DPI:            int   = 120                               # static

    def __init__(self, output_path: str = ""):
        """
        Initialise the plotter.

        Args:
            output_path (str): Where to save the figure. Uses DEFAULT_OUTPUT if empty.
        """
        self._output_path: str = output_path or self.DEFAULT_OUTPUT
        self._fig = None    # dynamic — created when plot() is called
        self._ax  = None

    # ── property ───────────────────────────────────────

    @property
    def output_path(self) -> str:
        """Path where the figure will be saved."""
        return self._output_path

    @output_path.setter
    def output_path(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("output_path cannot be empty.")
        self._output_path = value.strip()

    # ── plot ───────────────────────────────────────────

    def plot(self, results, x_min: float = 1.05, x_max: float = 5.0,
             n_points: int = 200, eps: float = 1e-6) -> str:
        """
        Create and save the comparison plot.

        Args:
            results    (list[SeriesResult]): Computed series results (table points).
            x_min      (float): Left boundary of x axis (must be > 1).
            x_max      (float): Right boundary of x axis.
            n_points   (int):   Number of smooth curve points.
            eps        (float): Precision for series curve.

        Returns:
            str: Path to the saved PNG file.
        """
        # ── continuous curves ───────────────────────────
        from task3_series.series_class import LnRatioSeries

        x_cont  = np.linspace(x_min, x_max, n_points)
        y_math  = [math.log((x + 1) / (x - 1)) for x in x_cont]

        series  = LnRatioSeries()
        y_series = []
        for x in x_cont:
            try:
                r = series.compute(float(x), eps)
                y_series.append(r.fx)
            except ValueError:
                y_series.append(float("nan"))

        # ── scatter points (table) ──────────────────────
        x_pts    = [r.x    for r in results]
        y_fx_pts = [r.fx   for r in results]
        y_mf_pts = [r.math_fx for r in results]

        # ── figure ─────────────────────────────────────
        self._fig, self._ax = plt.subplots(figsize=self.FIGURE_SIZE, dpi=self.DPI)
        ax = self._ax

        # Plot continuous curves
        ax.plot(x_cont, y_series, color="steelblue",  lw=2,
                label="Series F(x) [approx]", zorder=2)
        ax.plot(x_cont, y_math,   color="tomato",     lw=2,
                linestyle="--", label="Math F(x) [exact]", zorder=2)

        # Plot table data points
        if x_pts:
            ax.scatter(x_pts, y_fx_pts, color="steelblue",  s=60, zorder=5,
                       label="Series points (table)")
            ax.scatter(x_pts, y_mf_pts, color="darkred",    s=60, zorder=5,
                       marker="^", label="Math points (table)")

            # Annotate the first table point
            ax.annotate(
                f"x={x_pts[0]:.2f}\nF={y_fx_pts[0]:.4f}",
                xy=(x_pts[0], y_fx_pts[0]),
                xytext=(x_pts[0] + 0.3, y_fx_pts[0] + 0.1),
                arrowprops=dict(arrowstyle="->", color="grey"),
                fontsize=8, color="steelblue",
            )

        # ── coordinate axes through zero ───────────────
        ax.axhline(0, color="black", lw=0.8, zorder=1)
        ax.axvline(x_min, color="grey", lw=0.5, ls=":", zorder=1)

        # ── labels & formatting ─────────────────────────
        ax.set_title(
            r"$\ln\frac{x+1}{x-1} = 2\sum_{n=0}^{\infty}"
            r"\frac{1}{(2n+1)x^{2n+1}}$,  $|x|>1$",
            fontsize=13, pad=12
        )
        ax.set_xlabel("x",        fontsize=11)
        ax.set_ylabel("F(x)",     fontsize=11)
        ax.legend(fontsize=9,     loc="upper right")
        ax.grid(True, alpha=0.3)

        # Text annotation with formula note
        ax.text(0.98, 0.55,
                "LR4 — Task 3\nVariant 11",
                transform=ax.transAxes, fontsize=8,
                ha="right", va="top",
                bbox=dict(boxstyle="round,pad=0.3", fc="lightyellow", alpha=0.7))

        plt.tight_layout()

        # ── save ───────────────────────────────────────
        os.makedirs(os.path.dirname(self._output_path) or ".", exist_ok=True)
        plt.savefig(self._output_path, dpi=self.DPI, bbox_inches="tight")
        plt.show()
        plt.close(self._fig)
        print(f"  [График] Сохранён → {self._output_path}")
        return self._output_path

    def __repr__(self) -> str:
        return f"SeriesPlotter(output={self._output_path!r})"
