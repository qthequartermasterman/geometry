from geompy.core.Point import FastPoint as Point
from geompy.core.Point import FastPoint
from .test_constants import evaluate as sympify

from .test_Point import TestPoint

from symengine import Expr, Number


class TestFastPoint(TestPoint):
    def setUp(self) -> None:
        super().setUp()

    def assertEqual(self, *args, **kwargs):
        try:
            return super().assertEqual(*args, **kwargs)
        except AssertionError:
            # For numpy Fast Points, we need to do float evaluation, which is close but not quite.
            args = [float(arg.evalf()) if isinstance(arg, Expr) or isinstance(arg, Number) else arg for arg in args]
            return super().assertAlmostEqual(*args, **kwargs)