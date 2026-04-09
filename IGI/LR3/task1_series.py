# =============================================================================
# Lab Work #3: Standard Data Types, Collections, Functions, Modules
# File: task1_series.py — Power series for ln((x+1)/(x-1)), Variant 11
# Version: 1.0
# Developer: Student, Variant 11
# Date: 2025
# =============================================================================

import math
from utils import timer_decorator, input_float_constrained, print_separator

MAX_ITERATIONS = 500


# ─────────────────────────────────────────────
#  CORE COMPUTATION
# ─────────────────────────────────────────────

@timer_decorator
def compute_series(x, eps):
    """
    Compute ln((x+1)/(x-1)) using its power series expansion:

        ln((x+1)/(x-1)) = 2 * sum( 1 / ((2n+1) * x^(2n+1)) ), |x| > 1

    Stops when the absolute value of the current term is less than eps,
    or after MAX_ITERATIONS iterations.

    Args:
        x   (float): The argument of the function. Must satisfy |x| > 1.
        eps (float): The desired precision (e.g. 1e-6).

    Returns:
        tuple: (F_x, n_terms) where
            F_x     (float) — approximated value of the function,
            n_terms (int)   — number of terms summed.
    """
    total   = 0.0
    n_terms = 0

    for n in range(MAX_ITERATIONS):
        power = 2 * n + 1
        term  = 1.0 / (power * (x ** power))
        total += term
        n_terms += 1

        if abs(term) < eps:
            break

    return 2 * total, n_terms


def math_reference(x):
    """
    Compute the reference value of ln((x+1)/(x-1)) using the math module.

    Args:
        x (float): The argument. Must satisfy |x| > 1.

    Returns:
        float: The exact value computed by math.log.
    """
    return math.log((x + 1) / (x - 1))


# ─────────────────────────────────────────────
#  INPUT
# ─────────────────────────────────────────────

def get_x():
    """
    Prompt the user to enter x with the constraint |x| > 1.

    Returns:
        float: A valid x value satisfying |x| > 1.
    """
    return input_float_constrained(
        prompt      = "  Введите x (|x| > 1, например 2.0): ",
        condition   = lambda v: abs(v) > 1,
        error_msg   = "|x| должен быть больше 1."
    )


def get_eps():
    """
    Prompt the user to enter the precision eps with the constraint eps > 0.

    Returns:
        float: A positive precision value.
    """
    return input_float_constrained(
        prompt      = "  Enter precision eps (e.g. 0.0001): ",
        condition   = lambda v: v > 0,
        error_msg   = "eps must be a positive number."
    )


# ─────────────────────────────────────────────
#  OUTPUT
# ─────────────────────────────────────────────

def print_result(x, fx, math_fx, n_terms, eps):
    """
    Display the computation results in a formatted table.

    Args:
        x       (float): Argument value.
        fx      (float): Series-computed function value.
        math_fx (float): Reference value from math module.
        n_terms (int):   Number of terms used.
        eps     (float): Precision used.
    """
    col = 14  # column width
    print()
    print("  " + "-" * (col * 5 + 2))
    print(f"  {'x':^{col}}{'n':^{col}}{'F(x)':^{col}}{'Math F(x)':^{col}}{'eps':^{col}}")
    print("  " + "-" * (col * 5 + 2))
    print(f"  {x:^{col}.6f}{n_terms:^{col}}{fx:^{col}.6f}{math_fx:^{col}.6f}{eps:^{col}}")
    print("  " + "-" * (col * 5 + 2))


# ─────────────────────────────────────────────
#  MAIN TASK ENTRY POINT
# ─────────────────────────────────────────────

def run_task1():
    """
    Main entry point for Task 1.
    Prompts the user for x and eps, computes the power series
    approximation of ln((x+1)/(x-1)), and displays a result table.
    """
    print_separator("Task 1 — Power Series: ln((x+1)/(x-1))")
    print("  Formula: 2 * Σ 1/((2n+1)·xˆ(2n+1)),  |x| > 1")
    print(f"  Max iterations: {MAX_ITERATIONS}\n")

    x   = get_x()
    eps = get_eps()

    print()
    fx, n_terms = compute_series(x, eps)   # decorator prints timing here
    math_fx     = math_reference(x)

    print_result(x, fx, math_fx, n_terms, eps)
