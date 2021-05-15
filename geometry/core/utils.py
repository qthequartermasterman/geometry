from symengine import Expr, Eq
from sympy.simplify import sqrtdenest

from typing import Union
Expression = Union[Expr, str, int]  # Anything that is sympify-able


def symengine_equality(a: Expr, b: Expr):
    return Eq(a, b).simplify()


def optimized_simplify(expr: Expr) -> Expr:
    #return sqrtdenest(expr)
    return expr