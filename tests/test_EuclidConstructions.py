from unittest import TestCase

from geometry import Point, Line
from geometry.core.EuclidConstructions import check_if_points_on_same_side


class Test(TestCase):
    def test_check_if_points_on_same_side(self):
        a = Point(0, 0)
        b = Point(1, 0)
        c = Point(1, 1)
        d = Point(2, 2)
        e = Point(-1, -2)
        line1 = Line(a, b)
        self.assertTrue(check_if_points_on_same_side(line1, c, d))
        self.assertFalse(check_if_points_on_same_side(line1, c, e))

        line2 = Line(a, c)
        self.assertTrue(check_if_points_on_same_side(line2, b, e))

        self.assertRaises(ValueError, lambda:check_if_points_on_same_side(line1, a, c))
