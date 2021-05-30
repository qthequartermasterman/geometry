from symengine import Expr, Eq, sympify, nan
from sympy.simplify import sqrtdenest
from sympy import simplify

from functools import lru_cache

from typing import Union
Expression = Union[Expr, str, int, float]  # Anything that is sympify-able


@lru_cache
def is_nan(element: Expression):
    element = sympify(element)
    return isinstance(element, type(nan))


@lru_cache
def symengine_equality(a: Expr, b: Expr):
    return Eq(a, b).simplify()


@lru_cache
def optimized_simplify(expr: Expr) -> Expr:
    #return sqrtdenest(expr)
    return expr.expand()
    #return simplify(expr)
    #return sqrtdenest(expr).expand()

@lru_cache
def full_simplify(expr: Expr) -> Expr:
    return simplify(optimized_simplify(expr))


