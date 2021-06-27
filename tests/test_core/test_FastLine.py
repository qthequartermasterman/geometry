# For fast Line, we need to use numpy constants instead of sympy/symengine
from geometry.core.Point import FastPoint as Point
from geometry.core.Point import FastPoint
from geometry.core.Line import FastLine as Line
from geometry.core.Line import FastLine
from .test_constants import evaluate as sympify
from symengine import Expr, Number
from numpy import inf as oo
from numpy import inf as zoo

from .test_Line import TestLine
from .test_constants import coordinates


class TestFastLine(TestLine):
    def setUp(self) -> None:
        # super().setUp()
        self.point1 = Point(0, 0)
        self.point2 = Point(1, 0)
        self.line1 = Line(self.point1, self.point2, name='AB')
        self.coordinates = coordinates

    def assertEqual(self, *args, **kwargs):
        try:
            return super().assertEqual(*args, **kwargs)
        except AssertionError:
            # For numpy Fast Points, we need to do float evaluation, which is close but not quite.
            args = [float(arg.evalf()) if isinstance(arg, Expr) or isinstance(arg, Number) else arg for arg in args]
            return super().assertAlmostEqual(*args, **kwargs)

    def test_repr(self):
        self.assertEqual(repr(self.line1), 'Line AB through Point : (0.0, 0.0) and Point : (1.0, 0.0): y=0.0x+0.0')