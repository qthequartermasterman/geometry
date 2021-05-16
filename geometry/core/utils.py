from symengine import Expr, Eq, sympify, nan
from sympy.simplify import sqrtdenest

from typing import Union
Expression = Union[Expr, str, int]  # Anything that is sympify-able


def is_nan(element: Expression):
    element = sympify(element)
    return isinstance(element, type(nan))

def symengine_equality(a: Expr, b: Expr):
    return Eq(a, b).simplify()


def optimized_simplify(expr: Expr) -> Expr:
    #return sqrtdenest(expr)
    return expr.expand()

alphabet = list(map(chr, range(97, 123)))
