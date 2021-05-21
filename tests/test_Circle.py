from tests.test_constants import GeometryTestCase, coordinates

from geometry.core.Circle import Circle
from geometry.core.Point import Point

from symengine import zoo, oo

from itertools import combinations


class TestCircle(GeometryTestCase):
    def setUp(self) -> None:
        self.point1 = Point(0, 0)
        self.point2 = Point(1, 0)
        self.circle_from_point = Circle(self.point1, point2=self.point2, name='AB')
        self.circle_from_radius = Circle(self.point1, radius=1)
        self.coordinates = coordinates
        self.points = [Point(x, y) for x, y in coordinates]
        self.point_combinations = combinations(self.points, 2)

    def test_init_same_point(self):
        # Instantiating a circle with the same point twice should give a ValueError
        # Equivalently, instantiating a circle with radius 0 should give a ValueError
        with self.assertRaises(ValueError):
            Circle(self.point1, point2=self.point1)
            Circle(self.point1, radius=0)
            Circle(self.point1, radius='0')

    def test_repr(self):
        self.assertEqual(repr(self.circle_from_point), 'Circle AB with center Point : (0, 0) and radius 1')
        self.assertEqual(repr(self.circle_from_radius), 'Circle cr1 with center Point : (0, 0) and radius 1')

    def test_eq_with_radius_from_point2(self):
        for point1, point2 in self.point_combinations:
            radius = abs(point2-point1)
            self.assertEqual(Circle(point1, point2=point2), Circle(point1, radius=radius))
            self.assertEqual(Circle(point2, point2=point1), Circle(point2, radius=radius))

    def test_neq_not_symmetric(self):
        # Circle instantiation is not symmetric in the sense that reversing the center and second point do not give
        # equal circles
        self.assertNotEqual(Circle(self.point1, point2=self.point2), Circle(self.point2, point2=self.point1))

    def test_eq_name(self):
        self.assertEqual(Circle(self.point1, point2=self.point2, name='Name'),
                         Circle(self.point1, point2=self.point2))

    def test_eq_different_second_point_on_same_circle(self):
        center = Point(0,0)
        radius1 = Point(1,0)
        radius2 = Point(-1,0)
        radius3 = Point(0,1)
        radius4 = Point(0,-1)
        self.assertEqual(Circle(center, point2=radius1),
                         Circle(center, point2=radius2))
        self.assertEqual(Circle(center, point2=radius1),
                         Circle(center, point2=radius3))
        self.assertEqual(Circle(center, point2=radius1),
                         Circle(center, point2=radius4))
        self.assertEqual(Circle(center, point2=radius1),
                         Circle(center, radius=1))

    def test_neq(self):
        center = Point(0, 0)
        radius1 = Point(2, 0)
        radius2 = Point(1, 1)
        radius3 = Point(0, 1)
        radius4 = Point(0, 4)
        self.assertNotEqual(Circle(center, point2=radius1),
                         Circle(center, point2=radius2))
        self.assertNotEqual(Circle(center, point2=radius1),
                         Circle(center, point2=radius3))
        self.assertNotEqual(Circle(center, point2=radius1),
                         Circle(center, point2=radius4))
        self.assertNotEqual(Circle(center, point2=radius1),
                         Circle(center, radius=1))

    def test_hash(self):
        center = Point(0, 0)
        radius1 = Point(1, 0)
        radius2 = Point(-1, 0)
        radius3 = Point(0, 1)
        radius4 = Point(0, -1)
        self.assertHashEqual(Circle(center, point2=radius1),
                         Circle(center, point2=radius2))
        self.assertHashEqual(Circle(center, point2=radius1),
                         Circle(center, point2=radius3))
        self.assertHashEqual(Circle(center, point2=radius1),
                         Circle(center, point2=radius4))
        self.assertHashEqual(Circle(center, point2=radius1),
                         Circle(center, radius=1))

    def test_neq_hash(self):
        center = Point(0, 0)
        radius1 = Point(2, 0)
        radius2 = Point(1, 1)
        radius3 = Point(0, 1)
        radius4 = Point(0, 4)
        self.assertHashNotEqual(Circle(center, point2=radius1),
                            Circle(center, point2=radius2))
        self.assertHashNotEqual(Circle(center, point2=radius1),
                            Circle(center, point2=radius3))
        self.assertHashNotEqual(Circle(center, point2=radius1),
                            Circle(center, point2=radius4))
        self.assertHashNotEqual(Circle(center, point2=radius1),
                            Circle(center, radius=1))

    def test_contains(self):
        circle = Circle(Point(3,0), radius=5)
        self.assertIn(Point(8,0), circle)
        self.assertIn(Point(-2, 0), circle)
        self.assertIn(Point(3, 5), circle)
        self.assertIn(Point(3, -5), circle)

    def test_pickle(self):
        # For each of the coordinates, we will make points
        points = [Point(x, y) for x, y in self.coordinates]
        point_combinations = combinations(points, 2)
        # Iterative over every pair of points
        for point1, point2 in point_combinations:
            self.assertPickle(Circle(point1, point2=point2))
            radius = abs(point2-point1)
            self.assertPickle(Circle(point1, radius=radius))

    def test_plt_draw(self):
        self.fail()

    def test_simplify(self):
        self.fail()
