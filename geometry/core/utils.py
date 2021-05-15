from symengine import Expr, Eq
from sympy.simplify import sqrtdenest


def symengine_equality(a: Expr, b: Expr):
    return Eq(a, b).simplify()


def optimized_simplify(expr: Expr):
    #return sqrtdenest(expr)
    return expr