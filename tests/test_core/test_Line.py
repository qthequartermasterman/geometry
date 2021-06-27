from .test_constants import GeometryTestCase, coordinates

from geompy.core.Line import Line
from geompy.core.Point import Point

from symengine import zoo, oo

from itertools import combinations


class TestLine(GeometryTestCase):
    def assertEqual(self, left, right, *args, **kwargs):
        try:
            # Simplify first, since symengine equality currently doesn't evaluate properly.
            left = left.simplify()
            right = right.simplify()
            return super().assertEqual(left, right, *args, **kwargs)
        except AttributeError:
            return super().assertEqual(left, right, *args, **kwargs)

    def setUp(self) -> None:
        self.point1 = Point(0, 0)
        self.point2 = Point(1, 0)
        self.line1 = Line(self.point1, self.point2, name='AB')
        self.coordinates = coordinates

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
        # For each of the coordinates, we will make points
        points = [Point(x, y) for x, y in self.coordinates]
        point_combinations = combinations(points, 2)
        # Iterative over every pair of points
        for point1, point2 in point_combinations:
            self.assertEqual(abs(Line(point1, point2)), abs(point2 - point1))
            self.assertEqual(abs(Line(point2, point1)), abs(point1 - point2))

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

    def test_pickle(self):
        # For each of the coordinates, we will make points
        points = [Point(x, y) for x, y in self.coordinates]
        point_combinations = combinations(points, 2)
        # Iterative over every pair of points
        for point1, point2 in point_combinations:
            self.assertPickle(Line(point1, point2))

    def test_calculate_slope(self):
        # For each of the coordinates, we will make points
        points = [Point(x, y) for x, y in self.coordinates]
        point_combinations = combinations(points, 2)
        # Iterative over every pair of points
        for pair in point_combinations:
            # Slope should be equal to the slope formula for every pair above
            if pair[1].x != pair[0].x:
                slope = (pair[1].y - pair[0].y) / (pair[1].x - pair[0].x)
                # The above formula, when calculated this way will give a complex infinity in symengine
                if slope == zoo:
                    slope = oo
            else:
                slope = oo
            self.assertEqual(Line.calculate_slope(*pair), slope,
                             f'{pair} failed to get the correct slope')

    def test_calculate_intercept(self):
        # For each of the coordinates, we will make points
        points = [Point(x, y) for x, y in self.coordinates]
        point_combinations = combinations(points, 2)
        # Iterative over every pair of points
        for point1, point2 in point_combinations:
            slope = Line.calculate_slope(point1, point2)
            if slope == oo:
                intercept = oo
            else:
                intercept = point1.y - point1.x * slope
            self.assertEqual(Line.calculate_intercept(point1, point2), intercept,
                             f'{point1, point2} failed to get the correct intercept')
            self.assertEqual(Line.calculate_intercept(point1, point2, slope), intercept,
                             f'{point1, point2} failed to get the correct intercept, when given slope')

    def test_plt_draw(self):
        # self.fail()
        pass

    def test_simplify(self):
        # self.fail()
        pass
