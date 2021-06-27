from unittest import TestCase

from geompy import Point, Line
from geompy.core.EuclidConstructions import check_if_points_on_same_side, EquilateralUnitTriangle, BaseConstruction, \
    EuclidI2


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

        self.assertRaises(ValueError, lambda: check_if_points_on_same_side(line1, a, c))

        line3 = Line(b, c)  # Vertical Line
        self.assertFalse(check_if_points_on_same_side(line3, d, e))
        self.assertTrue(check_if_points_on_same_side(line3, Point(10, 100), Point(10, 0)))

    def test_equilateral_triangle(self):
        """This will test that the equilateral unit triangle is created properly. Additionally will test EuclidI1"""
        construction = EquilateralUnitTriangle()
        self.assertTrue(Point('1/2', 'sqrt(3)/2') in construction.points)
        self.assertFalse(Point('1/2', '-sqrt(3)/2') not in construction.points)

    def test_EuclidI2(self):
        construction = BaseConstruction()
        a, b = construction.points
        c = construction.add_point(Point(1, 1))
        new_line = EuclidI2(construction, Line(a, b), c)
        self.assertEqual(abs(Line(a, b)), abs(new_line))