"""
task4_main.py — Entry point for Task 4: Geometric Shapes (Variant 11).
Lab:     LR4 — Files, Classes, Serializers, Regex, Standard Libraries
Version: 1.0
Author:  Variant 11

Variant 11: Square with an equilateral triangle built on one of its sides.
"""

from utils import (print_separator, input_positive_float,
                   input_string_nonempty)
from task4_geometry.shapes import (
    GeometricShape, ColorMixin, EquilateralTriangle,
    Square, SquareWithTriangle,
)

OUTPUT_PATH = "output/task4_figure.png"


# ─────────────────────────────────────────────
#  INPUT
# ─────────────────────────────────────────────

def get_side() -> float:
    """
    Prompt the user for a positive side length a.

    Returns:
        float: Positive side length.
    """
    return input_positive_float("  Введите длину стороны a (> 0): ")


def get_color(prompt: str, default: str) -> str:
    """
    Prompt the user for a color name, using default if empty.

    Args:
        prompt  (str): Input prompt.
        default (str): Default color if user just presses Enter.

    Returns:
        str: Color name string.
    """
    raw = input(f"  {prompt} [по умолчанию: {default}]: ").strip().lower()
    return raw if raw else default


def get_label() -> str:
    """
    Prompt for an optional text label.

    Returns:
        str: Label string (may be empty).
    """
    return input("  Текст подписи (необязательно, Enter — пропустить): ").strip()


# ─────────────────────────────────────────────
#  DEMO OOP FEATURES
# ─────────────────────────────────────────────

def demo_oop(a: float) -> None:
    """
    Demonstrate OOP features: polymorphism, magic methods, inheritance.

    Args:
        a (float): Side length used for demo objects.
    """
    sq  = Square(a, "blue")
    tri = EquilateralTriangle(a, "orange")

    print("\n  ── Демонстрация ООП ──")

    print(f"\n  str(Square)    : {sq}")
    print(f"  repr(Square)   : {repr(sq)}")
    print(f"  str(Triangle)  : {tri}")

    shapes: list[GeometricShape] = [sq, tri]
    print("\n  Полиморфизм — area() для разных фигур:")
    for shape in shapes:
        print(f"    {shape.__class__.__name__:25s} площадь = {shape.area():.4f}")

    sq2         = Square(a * 0.5, "red")
    sq_combined = sq + sq2
    print(f"\n  __add__: Square({a}) + Square({a*0.5:.2f})"
          f" = Square со стороной {sq_combined.a:.4f} (суммарная площадь)")

    sq3 = Square(a, "green")
    print(f"  __eq__ : Square(a={a}) == Square(a={a})   → {sq == sq3}")
    print(f"  __eq__ : Square(a={a}) == Square(a={a*2}) → {sq == Square(a*2)}")

    print(f"\n  Square.get_shape_name()         : {Square.get_shape_name()}")
    print(f"  Triangle.get_shape_name()       : {EquilateralTriangle.get_shape_name()}")
    print(f"  GeometricShape.get_shape_count(): {GeometricShape.get_shape_count()}")

    print(f"\n  Свойства Square  : периметр = {sq.perimeter:.4f}")
    print(f"  Свойства Triangle: высота   = {tri.height:.4f}")

    sq.color = "teal"
    print(f"  Смена цвета через сеттер: sq.color = '{sq.color}'")


# ─────────────────────────────────────────────
#  MAIN TASK ENTRY POINT
# ─────────────────────────────────────────────

def run_task4() -> None:
    """
    Main entry point for Task 4 — Geometric Shapes.

    Prompts for side length, colors, and a label.
    Demonstrates all OOP features, then draws and saves the composite figure.
    """
    print_separator("Задание 4 — Геометрические фигуры (Вариант 11)")
    print("  Фигура: квадрат с равносторонним треугольником на одной из сторон.\n")

    a         = get_side()
    sq_color  = get_color("Цвет квадрата",      "steelblue")
    tri_color = get_color("Цвет треугольника",   "orange")
    label     = get_label()

    figure = SquareWithTriangle(a, sq_color, tri_color, label)

    print(f"\n  {figure}")
    print(f"  repr: {repr(figure)}")

    demo_oop(a)

    print("\n  Строим фигуру...")
    figure.draw(OUTPUT_PATH)
    print(f"  Фигура сохранена: {OUTPUT_PATH}")
