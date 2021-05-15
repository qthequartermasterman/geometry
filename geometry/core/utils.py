from symengine import Expr, Eq


def symengine_equality(a: Expr, b: Expr):
    return Eq(a, b).simplify()