from unittest import TestCase

from geometry.core.Line import Line
from geometry.core.Point import Point


class TestLine(TestCase):
    def assertHashEqual(self, object1, object2, *args, **kwargs):
        return self.assertEqual(hash(object1), hash(object2), *args, **kwargs)

    def assertHashNotEqual(self, object1, object2, *args, **kwargs):
        return self.assertNotEqual(hash(object1), hash(object2), *args, **kwargs)

    def setUp(self) -> None:
        self.point1 = Point(0, 0)
        self.point2 = Point(1, 0)
        self.line1 = Line(self.point1, self.point2, name='AB')

    def test_init_same_point(self):
        # Instantiating a line with the same point twice should give a TypeError
        self.assertRaises(TypeError, Line, (self.point1, self.point1))

    def test_repr(self):
        self.assertEqual(repr(self.line1), 'Line AB through Point : (0, 0) and Point : (1, 0): y=0x+0')

    def test_eq(self):
        point0 = Point(0, 0)
        point3 = Point(2, 0)
        point4 = Point(-1, 0)
        point5 = Point(1, 1)
        point6 = Point(2, 1)
        point7 = Point(-1, 1)
        point8 = Point(2, 2)
        point9 = Point(3, 3)

        # Horizontal lines on the x-axis
        self.assertEqual(self.line1, Line(self.point1, self.point2))  # Test without name
        self.assertEqual(self.line1, Line(self.point2, self.point1))  # Test with reversed points
        self.assertEqual(self.line1, Line(self.point1, point3))  # Test with other points on same line
        self.assertEqual(self.line1, Line(point4, point3))  # Test with other points on same line

        # Horizontal lines not on the x-axis
        self.assertEqual(Line(point5, point6),
                         Line(point5, point6, name='ABC'))  # Test without name
        self.assertEqual(Line(point5, point6),
                         Line(point6, point5))  # Test with reversed points
        self.assertEqual(Line(point5, point6),
                         Line(point5, point7))  # Test with other points on same line
        self.assertEqual(Line(point5, point6),
                         Line(point6, point7))  # Test with other points on same line

        # Sloped lines
        self.assertEqual(Line(point0, point5),
                         Line(point0, point5, name='ABC'))  # Test without name
        self.assertEqual(Line(point0, point5),
                         Line(point5, point0))  # Test with reversed points
        self.assertEqual(Line(point0, point5),
                         Line(point5, point8))  # Test with other points on same line
        self.assertEqual(Line(point0, point5),
                         Line(point8, point9))  # Test with other points on same line

        # Vertical lines on the y-axis
        point10 = Point(0, 1)
        point11 = Point(0, 2)
        point12 = Point(0, 3)
        self.assertEqual(Line(point0, point10),
                         Line(point0, point10, name='ABC'))  # Test without name
        self.assertEqual(Line(point0, point10),
                         Line(point10, point0))  # Test with reversed points
        self.assertEqual(Line(point0, point10),
                         Line(point0, point11))  # Test with other points on same line
        self.assertEqual(Line(point0, point10),
                         Line(point11, point12))  # Test with other points on same line

        # Vertical lines not on the y-axis
        point13 = Point(1, 1)
        point14 = Point(2, 2)
        point15 = Point(3, 3)
        self.assertEqual(Line(point0, point13),
                         Line(point0, point13, name='ABC'))  # Test without name
        self.assertEqual(Line(point0, point13),
                         Line(point13, point0))  # Test with reversed points
        self.assertEqual(Line(point0, point13),
                         Line(point0, point14))  # Test with other points on same line
        self.assertEqual(Line(point0, point13),
                         Line(point14, point15))  # Test with other points on same line

    def test_neq(self):
        self.assertNotEqual(Line(Point(0, 0), Point(0, 1)),
                            Line(Point(0, 0), Point(1, 1)))
        self.assertNotEqual(Line(Point(0, 0), Point(0, 1)),
                            Line(Point(-1, 0), Point(1, 1)))
        self.assertNotEqual(Line(Point(0, 0), Point(0, 1)),
                            Line(Point(1, 0), Point(1, 1)))
        self.assertNotEqual(Line(Point(2, 0), Point(0, 1)),
                            Line(Point(2, 0), Point(1, 1)))

    def test_hash(self):
        point0 = Point(0, 0)
        point3 = Point(2, 0)
        point4 = Point(-1, 0)
        point5 = Point(1, 1)
        point6 = Point(2, 1)
        point7 = Point(-1, 1)
        point8 = Point(2, 2)
        point9 = Point(3, 3)

        # Horizontal lines on the x-axis
        self.assertHashEqual(self.line1, Line(self.point1, self.point2))  # Test without name
        self.assertHashEqual(self.line1, Line(self.point2, self.point1))  # Test with reversed points
        self.assertHashEqual(self.line1, Line(self.point1, point3))  # Test with other points on same line
        self.assertHashEqual(self.line1, Line(point4, point3))  # Test with other points on same line

        # Horizontal lines not on the x-axis
        self.assertHashEqual(Line(point5, point6),
                             Line(point5, point6, name='ABC'))  # Test without name
        self.assertHashEqual(Line(point5, point6),
                             Line(point6, point5))  # Test with reversed points
        self.assertHashEqual(Line(point5, point6),
                             Line(point5, point7))  # Test with other points on same line
        self.assertHashEqual(Line(point5, point6),
                             Line(point6, point7))  # Test with other points on same line

        # Sloped lines
        self.assertHashEqual(Line(point0, point5),
                             Line(point0, point5, name='ABC'))  # Test without name
        self.assertHashEqual(Line(point0, point5),
                             Line(point5, point0))  # Test with reversed points
        self.assertHashEqual(Line(point0, point5),
                             Line(point5, point8))  # Test with other points on same line
        self.assertHashEqual(Line(point0, point5),
                             Line(point8, point9))  # Test with other points on same line

        # Vertical lines on the y-axis
        point10 = Point(0, 1)
        point11 = Point(0, 2)
        point12 = Point(0, 3)
        self.assertHashEqual(Line(point0, point10),
                             Line(point0, point10, name='ABC'))  # Test without name
        self.assertHashEqual(Line(point0, point10),
                             Line(point10, point0))  # Test with reversed points
        self.assertHashEqual(Line(point0, point10),
                             Line(point0, point11))  # Test with other points on same line
        self.assertHashEqual(Line(point0, point10),
                             Line(point11, point12))  # Test with other points on same line

        # Vertical lines not on the y-axis
        point13 = Point(1, 1)
        point14 = Point(2, 2)
        point15 = Point(3, 3)
        self.assertHashEqual(Line(point0, point13),
                             Line(point0, point13, name='ABC'))  # Test without name
        self.assertHashEqual(Line(point0, point13),
                             Line(point13, point0))  # Test with reversed points
        self.assertHashEqual(Line(point0, point13),
                             Line(point0, point14))  # Test with other points on same line
        self.assertHashEqual(Line(point0, point13),
                             Line(point14, point15))  # Test with other points on same line

    def test_neq_hash(self):
        self.assertHashNotEqual(Line(Point(0, 0), Point(0, 1)),
                                Line(Point(0, 0), Point(1, 1)))
        self.assertHashNotEqual(Line(Point(0, 0), Point(0, 1)),
                                Line(Point(-1, 0), Point(1, 1)))
        self.assertHashNotEqual(Line(Point(0, 0), Point(0, 1)),
                                Line(Point(1, 0), Point(1, 1)))
        self.assertHashNotEqual(Line(Point(2, 0), Point(0, 1)),
                                Line(Point(2, 0), Point(1, 1)))

    def test_abs(self):
        self.fail()

    def test_contains(self):
        self.assertIn(Point(0, 0), self.line1)
        self.assertIn(Point(1, 0), self.line1)
        self.assertIn(Point(-3, 0), self.line1)
        self.assertIn(Point(-10, 0), self.line1)
        self.assertNotIn(Point(1, 1), self.line1)

        line2 = Line(Point(3, 2), Point(1, 1))
        self.assertIn(Point(2, '3/2'), line2)
        self.assertIn(Point(0, '1/2'), line2)
        self.assertNotIn(Point(3, 1), line2)

        vertical_line = Line(Point(2, 2), Point(2, 0))
        self.assertIn(Point(2, 2), vertical_line)
        self.assertIn(Point(2, 100), vertical_line)
        self.assertNotIn(Point(0, -100), vertical_line)

    def test_get_state(self):
        self.fail()

    def test_set_state(self):
        self.fail()

    def test_calculate_slope(self):
        self.fail()

    def test_calculate_intercept(self):
        self.fail()

    def test_plt_draw(self):
        self.fail()

    def test_simplify(self):
        self.fail()
