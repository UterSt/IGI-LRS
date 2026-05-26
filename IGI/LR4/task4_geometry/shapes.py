"""
shapes.py — Geometric shape classes for Task 4 (Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Variant 11: Draw a square, with an equilateral triangle built on one of its sides.

Class hierarchy:
  ColorMixin           — mixin providing color property
  GeometricShape (ABC) — abstract base with abstract area()
      └── Square       — concrete square with class-method name()
              └── SquareWithTriangle — composite: square + equilateral triangle

  EquilateralTriangle  — separate concrete triangle class (used internally)

Demonstrates ALL required OOP features:
  ✓ Static + dynamic attributes
  ✓ Polymorphism (area() override at each level)
  ✓ Magic methods (__str__, __repr__, __eq__, __add__)
  ✓ super()
  ✓ Getters and setters (@property)
  ✓ Class properties (@classmethod)
  ✓ Mixins (ColorMixin)
"""

import math
import os
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
import numpy as np


# ─────────────────────────────────────────────
#  MIXIN
# ─────────────────────────────────────────────

class ColorMixin:
    """
    Mixin that adds a validated color property to any shape class.

    Demonstrates mixin usage and @property setter.
    """

    VALID_COLORS: tuple = (          # static attribute
        "red", "blue", "green", "yellow", "orange",
        "purple", "pink", "cyan", "magenta", "brown",
        "grey", "white", "black", "gold", "teal",
    )

    def __init__(self, color: str = "blue"):
        self._color: str = ""        # dynamic attribute
        self.color = color           # triggers setter

    @property
    def color(self) -> str:
        """Fill color of the shape."""
        return self._color

    @color.setter
    def color(self, value: str) -> None:
        """
        Set the fill color; accepts any named color (validated loosely).

        Args:
            value (str): Color name.

        Raises:
            ValueError: If value is not a non-empty string.
        """
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Color must be a non-empty string.")
        self._color = value.strip().lower()


# ─────────────────────────────────────────────
#  ABSTRACT BASE
# ─────────────────────────────────────────────

class GeometricShape(ABC):
    """
    Abstract base class for all geometric figures.

    Enforces implementation of area() in every concrete subclass.
    """

    _shape_count: int = 0           # static attribute — total shapes created

    def __init__(self):
        GeometricShape._shape_count += 1

    @abstractmethod
    def area(self) -> float:
        """
        Compute and return the area of the shape.

        Returns:
            float: Area in square units.
        """

    @classmethod
    def get_shape_count(cls) -> int:
        """
        Return the total number of GeometricShape instances created.

        Returns:
            int: Instance count.
        """
        return cls._shape_count

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(area={self.area():.4f})"


# ─────────────────────────────────────────────
#  EQUILATERAL TRIANGLE
# ─────────────────────────────────────────────

class EquilateralTriangle(GeometricShape, ColorMixin):
    """
    Equilateral triangle with side a.

    Inherits GeometricShape (forces area()) and ColorMixin (adds color).
    Uses super() to initialise both parents cleanly.
    """

    _shape_name: str = "Equilateral Triangle"   # static attribute

    def __init__(self, a: float, color: str = "orange"):
        """
        Initialise an equilateral triangle.

        Args:
            a     (float): Side length (must be > 0).
            color (str):   Fill color.

        Raises:
            ValueError: If a <= 0.
        """
        GeometricShape.__init__(self)
        ColorMixin.__init__(self, color)
        self._a: float = 0.0        # dynamic attribute
        self.a = a                  # use setter

    # ── property ───────────────────────────────────────

    @property
    def a(self) -> float:
        """Side length."""
        return self._a

    @a.setter
    def a(self, value: float) -> None:
        if value <= 0:
            raise ValueError(f"Side 'a' must be positive, got {value}.")
        self._a = float(value)

    @property
    def height(self) -> float:
        """Height of the equilateral triangle."""
        return self._a * math.sqrt(3) / 2

    # ── class method ───────────────────────────────────

    @classmethod
    def get_shape_name(cls) -> str:
        """Return the canonical name of this shape type."""
        return cls._shape_name

    # ── area ───────────────────────────────────────────

    def area(self) -> float:
        """
        Area = (√3 / 4) · a²

        Returns:
            float: Triangle area.
        """
        return (math.sqrt(3) / 4) * (self._a ** 2)

    # ── info string ────────────────────────────────────

    def info(self) -> str:
        """
        Return a formatted description of the triangle.

        Returns:
            str: Description using str.format().
        """
        return (
            "{name}: side={a:.4f}, height={h:.4f}, "
            "area={area:.4f}, color={color}"
        ).format(
            name  = self._shape_name,
            a     = self._a,
            h     = self.height,
            area  = self.area(),
            color = self._color,
        )

    # ── magic methods ──────────────────────────────────

    def __str__(self) -> str:
        return self.info()

    def __repr__(self) -> str:
        return f"EquilateralTriangle(a={self._a}, color='{self._color}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, EquilateralTriangle):
            return NotImplemented
        return math.isclose(self._a, other._a)


# ─────────────────────────────────────────────
#  SQUARE
# ─────────────────────────────────────────────

class Square(GeometricShape, ColorMixin):
    """
    Square with side a.

    Inherits GeometricShape and ColorMixin.
    The shape name is a class-level datum returned by a class method.
    """

    _shape_name: str = "Square"     # static attribute

    def __init__(self, a: float, color: str = "blue"):
        """
        Initialise a square.

        Args:
            a     (float): Side length (> 0).
            color (str):   Fill color.
        """
        GeometricShape.__init__(self)
        ColorMixin.__init__(self, color)
        self._a: float = 0.0        # dynamic attribute
        self.a = a

    # ── property ───────────────────────────────────────

    @property
    def a(self) -> float:
        """Side length."""
        return self._a

    @a.setter
    def a(self, value: float) -> None:
        if value <= 0:
            raise ValueError(f"Side 'a' must be positive, got {value}.")
        self._a = float(value)

    @property
    def perimeter(self) -> float:
        """Perimeter = 4a."""
        return 4 * self._a

    # ── class method ───────────────────────────────────

    @classmethod
    def get_shape_name(cls) -> str:
        """Return the canonical name of this shape type."""
        return cls._shape_name

    # ── area (polymorphism) ────────────────────────────

    def area(self) -> float:
        """
        Area = a²

        Returns:
            float: Square area.
        """
        return self._a ** 2

    # ── info string ────────────────────────────────────

    def info(self) -> str:
        """
        Return a formatted description of the square.

        Returns:
            str: Description using str.format().
        """
        return (
            "{name}: side={a:.4f}, perimeter={p:.4f}, "
            "area={area:.4f}, color={color}"
        ).format(
            name  = self._shape_name,
            a     = self._a,
            p     = self.perimeter,
            area  = self.area(),
            color = self._color,
        )

    # ── magic methods ──────────────────────────────────

    def __str__(self) -> str:
        return self.info()

    def __repr__(self) -> str:
        return f"Square(a={self._a}, color='{self._color}')"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Square):
            return NotImplemented
        return math.isclose(self._a, other._a)

    def __add__(self, other):
        """Combine two squares into one with area = sum of both areas."""
        if not isinstance(other, Square):
            raise TypeError(f"Cannot add Square and {type(other).__name__}.")
        combined_a = math.sqrt(self.area() + other.area())
        return Square(combined_a, self._color)


# ─────────────────────────────────────────────
#  SQUARE WITH TRIANGLE (Variant 11 shape)
# ─────────────────────────────────────────────

class SquareWithTriangle(Square):
    """
    Composite figure: a square with an equilateral triangle built on its top side.

    Variant 11: 'Build a square, on one side of which an equilateral triangle
    with side a is constructed.'

    The triangle shares side a with the top edge of the square.
    Total combined area = square.area() + triangle.area().
    """

    _shape_name: str = "Square + Equilateral Triangle"   # static attribute

    def __init__(self, a: float, color: str = "blue", tri_color: str = "orange",
                 label: str = ""):
        """
        Initialise the composite figure.

        Args:
            a         (float): Common side length.
            color     (str):   Square fill color.
            tri_color (str):   Triangle fill color.
            label     (str):   Optional text label drawn on the figure.
        """
        super().__init__(a, color)                          # super() → Square
        self._triangle: EquilateralTriangle = EquilateralTriangle(a, tri_color)
        self._label: str = label                            # dynamic attribute

    # ── property ───────────────────────────────────────

    @property
    def triangle(self) -> EquilateralTriangle:
        """The equilateral triangle component."""
        return self._triangle

    @property
    def label(self) -> str:
        """Text label for the figure."""
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        self._label = str(value)

    # ── area (polymorphism — overrides Square.area) ────

    def area(self) -> float:
        """
        Combined area = square area + triangle area (polymorphic override).

        Returns:
            float: Total area of both shapes.
        """
        return super().area() + self._triangle.area()   # super() for square area

    # ── draw ───────────────────────────────────────────

    def draw(self, output_path: str = "output/task4_figure.png") -> str:
        """
        Draw the composite figure with matplotlib and save to a file.

        Args:
            output_path (str): Path where the PNG is saved.

        Returns:
            str: Saved file path.
        """
        a   = self._a
        tri = self._triangle

        # ── vertices ───────────────────────────────────
        # Square: bottom-left at origin
        sq_verts = np.array([[0, 0], [a, 0], [a, a], [0, a], [0, 0]])

        # Triangle: on top side of square (from (0,a) to (a,a))
        tri_apex = np.array([a / 2, a + tri.height])
        tri_verts = np.array([[0, a], [a, a], tri_apex, [0, a]])

        # ── figure ─────────────────────────────────────
        fig, ax = plt.subplots(figsize=(7, 8), dpi=110)

        sq_patch  = Polygon(sq_verts[:-1],  closed=True,
                            facecolor=self._color,       alpha=0.55,
                            edgecolor="navy",            lw=2, label="Square")
        tri_patch = Polygon(tri_verts[:-1], closed=True,
                            facecolor=tri.color,         alpha=0.55,
                            edgecolor="darkorange",      lw=2, label="Triangle")

        ax.add_patch(sq_patch)
        ax.add_patch(tri_patch)

        # ── dimension annotations ───────────────────────
        ax.annotate("", xy=(a, -0.15), xytext=(0, -0.15),
                    arrowprops=dict(arrowstyle="<->", color="black", lw=1.2))
        ax.text(a / 2, -0.25, f"a = {a:.2f}", ha="center", fontsize=10)

        ax.annotate("", xy=(-0.2, a), xytext=(-0.2, 0),
                    arrowprops=dict(arrowstyle="<->", color="black", lw=1.2))
        ax.text(-0.45, a / 2, f"a = {a:.2f}", ha="center", fontsize=10,
                rotation=90)

        h_total = a + tri.height
        ax.annotate("", xy=(a + 0.2, h_total), xytext=(a + 0.2, a),
                    arrowprops=dict(arrowstyle="<->", color="darkorange", lw=1.2))
        ax.text(a + 0.55, a + tri.height / 2,
                f"h = {tri.height:.2f}", ha="center", fontsize=9, color="darkorange",
                rotation=90)

        # ── label text ──────────────────────────────────
        lbl = self._label or f"a = {a:.2f}"
        ax.text(a / 2, a / 2,   lbl,      ha="center", va="center",
                fontsize=11, color="navy",   fontweight="bold")
        ax.text(a / 2, a + tri.height / 3, "△",
                ha="center", va="center", fontsize=20, color="saddlebrown")

        # ── area info box ───────────────────────────────
        info_text = (
            f"Square area : {super().area():.4f}\n"
            f"Triangle area: {self._triangle.area():.4f}\n"
            f"Total area   : {self.area():.4f}"
        )
        ax.text(0.98, 0.98, info_text,
                transform=ax.transAxes, fontsize=9,
                ha="right", va="top",
                bbox=dict(boxstyle="round,pad=0.4", fc="lightyellow", alpha=0.85))

        # ── axes ───────────────────────────────────────
        margin = 0.7
        ax.set_xlim(-margin, a + margin)
        ax.set_ylim(-0.5,    h_total + margin)
        ax.set_aspect("equal")
        ax.axhline(0, color="grey", lw=0.5, ls=":")
        ax.axvline(0, color="grey", lw=0.5, ls=":")
        ax.set_xlabel("x", fontsize=10)
        ax.set_ylabel("y", fontsize=10)
        ax.set_title(
            f"{self._shape_name}\n(side a = {a:.2f}, color={self._color})",
            fontsize=12, pad=10
        )
        ax.legend(loc="upper left", fontsize=9)
        ax.grid(True, alpha=0.25)

        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        plt.savefig(output_path, dpi=110, bbox_inches="tight")
        plt.show()
        plt.close(fig)
        print(f"  [График] Фигура сохранена → {output_path}")
        return output_path

    # ── info / magic ────────────────────────────────────

    def info(self) -> str:
        """Full description including both components."""
        return (
            "{name}: side={a:.4f}, "
            "square_area={sq:.4f}, triangle_area={tr:.4f}, "
            "total_area={tot:.4f}, "
            "square_color={sc}, triangle_color={tc}"
        ).format(
            name = self._shape_name,
            a    = self._a,
            sq   = super().area(),
            tr   = self._triangle.area(),
            tot  = self.area(),
            sc   = self._color,
            tc   = self._triangle.color,
        )

    def __str__(self) -> str:
        return self.info()

    def __repr__(self) -> str:
        return (f"SquareWithTriangle(a={self._a}, "
                f"color='{self._color}', tri_color='{self._triangle.color}')")
