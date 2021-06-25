from .test_constants import GeometryTestCase, coordinates
from geometry.core import Point
import numpy as np
from symengine import sympify, nan, Expr, Number


class TestPoint(GeometryTestCase):
    def setUp(self) -> None:
        self.point1_int = Point(2, 3)
        self.point1_sympy_int = Point('2', '3')
        self.point1_sympy_expr = Point('sqrt(2)**2', 'sqrt(3)**2')
        self.point1_name = Point(2, 3, 'Name')
        self.point1_list = [2, 3]
        self.point1_tuple = (2, 3)
        self.point1_np = np.array([2, 3])
        self.point2_expanded = Point(
            'sqrt((33/8 + (1/24)*sqrt(27)*sqrt(63))**2 + ((3/8)*sqrt(27) + (-1/8)*sqrt(63))**2)',
            'sqrt((33/8 + (1/24)*sqrt(27)*sqrt(63))**2 + ((3/8)*sqrt(27) + (-1/8)*sqrt(63))**2)')
        self.point2_simplified = Point('3*sqrt(2)/4 + 3*sqrt(42)/4', '3*sqrt(2)/4 + 3*sqrt(42)/4')
        self.coordinates = coordinates

    def test_nan_init(self):
        # Trying to initialize a coordinate as NaN should raise TypeError
        self.assertRaises(TypeError, Point, (nan, nan))
        self.assertRaises(TypeError, Point, (0, nan))
        self.assertRaises(TypeError, Point, (nan, 0))
        self.assertRaises(TypeError, Point, (float('nan'), float('nan')))
        self.assertRaises(TypeError, Point, (float('nan'), 1))
        self.assertRaises(TypeError, Point, (1, float('nan')))
        self.assertRaises(TypeError, Point, (np.nan, 1))
        self.assertRaises(TypeError, Point, (1, np.nan))
        self.assertRaises(TypeError, Point, (np.nan, np.nan))

    def test_repr(self):
        rep = repr(self.point1_int)
        self.assertIn(self.point1_int.name, rep)
        self.assertIn(repr(self.point1_int.x), rep)
        self.assertIn(repr(self.point1_int.y), rep)

    def test_equals(self):
        # We only need to test each against the first, because equality is transitive
        # Points with different names but equivalent coordinates are still equivalent.
        for other in (self.point1_int, self.point1_sympy_int, self.point1_sympy_expr, self.point1_name):
            self.assertEqual(self.point1_int, other)

        # Make sure that a non-point does not return equal
        for other in (self.point1_list, self.point1_tuple, self.point1_np):
            self.assertNotEqual(self.point1_int, other)

        self.assertEqual(self.point2_expanded, self.point2_simplified)

    def test_hash(self):
        # Hash should just be the hash of the tuple (x,y) for each point. Name should not affect hash.
        # Points with different names but equivalent coordinates are still equivalent.
        for other in (self.point1_sympy_int, self.point1_sympy_expr, self.point1_name):
            self.assertEqual(hash(self.point1_int), hash(other))

    def test_hash_simplified(self):
        # Ideally, two equivalent (although complicated they yield the same canonical simplification) expressions should
        # give the same hash.
        self.assertEqual(hash(self.point2_expanded), hash(self.point2_simplified))

    def test_add(self):
        self.assertEqual(self.point1_int + self.point1_int, Point(4, 6))
        self.assertEqual(Point(0, 0) + Point(0, 0), Point(0, 0))
        self.assertEqual(Point('sqrt(2)', 0) + Point(0, 'sqrt(2)'), Point('sqrt(2)', 'sqrt(2)'))
        self.assertEqual(Point('sqrt(2)', 3) + Point('sqrt(3)', -2), Point('sqrt(2) + sqrt(3)', 1))
        self.assertEqual(Point('cos(3)', -9) + Point('1', -1), Point('cos(3)+1', -10))

    def test_subtract(self):
        self.assertEqual(self.point1_int - self.point1_int, Point(0, 0))
        self.assertEqual(Point(0, 0) - Point(0, 0), Point(0, 0))
        self.assertEqual(Point('sqrt(2)', 0) - Point(0, 'sqrt(2)'), Point('sqrt(2)', '-sqrt(2)'))
        self.assertEqual(Point('sqrt(2)', 3) - Point('sqrt(3)', -2), Point('sqrt(2) - sqrt(3)', 5))
        self.assertEqual(Point('cos(3)', -9) - Point('1', -1), Point('cos(3)-1', -8))

    def test_multiply(self):
        self.assertEqual(Point(0, 0) * Point(1, 1), 0)
        self.assertEqual(Point(1, 1) * Point(2, 2), 4)
        self.assertEqual(Point(-3, -5) * Point(7, -11), -21 + 55)

        self.assertEqual(6 * Point(2, 3), Point(12, 18))
        self.assertEqual(Point(2, 3) * 6, Point(12, 18))

    def test_abs(self):
        point_magnitude = {(0, 0): 0,
                           (1, 1): 'sqrt(2)',
                           (2, 3): 'sqrt(13)',
                           (-3, -1): 'sqrt(10)',
                           ('sqrt(3)', 'sqrt(2)'): 'sqrt(5)'}

        for point, magnitude in point_magnitude.items():
            magnitude = sympify(magnitude)
            self.assertEqual(abs(Point(*point)), magnitude)

    def test_plt_draw(self):
        #self.fail()
        pass

    def test_numpy(self):
        array1 = Point(2, 3).numpy()
        array2 = Point('sqrt(2)', 'sqrt(3)').numpy()
        self.assertEqual(array1[0], 2)
        self.assertEqual(array1[1], 3)
        self.assertAlmostEqual(array2[0], 1.4142135623730951)
        self.assertAlmostEqual(array2[1], 1.7320508075688772)

    def test_normalize(self):
        self.assertEqual(abs(Point(2, 3).normalize()), 1)

    def test_simplify(self):
        #self.fail()
        pass

    def test_pickle(self):
        # For each of the coordinates, we will make points
        points = [Point(x, y) for x, y in self.coordinates]
        # Iterative over each point
        for point in points:
            self.assertPickle(point)



