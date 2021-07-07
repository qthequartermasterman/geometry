from .test_constants import GeometryTestCase

from geompy import Angle, Line, Point
from geompy.core.EuclidConstructions import EquilateralUnitTriangle
from math import pi


class AngleTest(GeometryTestCase):
    def test_angle_measure(self):
        """
            c
          / |
         /  |
        a---b
        """
        a = Point(0, 0)
        b = Point(1, 0)
        c = Point(1, 1)
        line_ab = Line(a, b)
        line_ac = Line(a, c)
        angle_abc = Angle(line_ab, line_ac)
        self.assertAlmostEqual(pi / 4, angle_abc.measure)

    def test_angle_init(self):
        """
            c
          / |
         /  |
        a---b
        """
        a = Point(0, 0)
        b = Point(1, 0)
        c = Point(1, 1)
        line_ab = Line(a, b)
        line_ac = Line(a, c)
        angle_abc = Angle(line_ab, line_ac)
        self.assertEqual(a, angle_abc.vertex_point)

    def test_angle_equality(self):
        """
                    c
                  / |
                 /  |
                a---b
                """

        a = Point(0, 0)
        b = Point(1, 0)
        c = Point('1/2', 'sqrt(3)/2')
        # Note, that we double up these line definitions so we can orient all of our angles inwards.
        line_ab, line_ba = Line(a, b), Line(b, a)
        line_ac, line_ca = Line(a, c), Line(c, a)
        line_bc, line_cb = Line(b, c), Line(c, b)
        angle_cab = Angle(line_ac, line_ab)
        angle_cba = Angle(line_bc, line_ba)
        angle_acb = Angle(line_ca, line_cb)

        self.assertEqual(angle_acb, angle_cab)
        self.assertEqual(angle_acb, angle_cba)

    def test_supplementary_angles(self):
        a = Point(0, 0)
        b = Point(1, 0)
        c = Point(1, 1)
        line_ab, line_ba = Line(a, b), Line(b, a)
        line_ac, line_ca = Line(a, c), Line(c, a)
        angle_cab = Angle(line_ac, line_ab)
        angle_bacprime = Angle(line_ab, line_ca)
        angle_cabprime = Angle(line_ac, line_ba)
        self.assertEqual(pi, angle_cab.measure+angle_bacprime.measure)
        self.assertEqual(pi, angle_cab.measure+angle_cabprime.measure)

    def test_opposite_interior_angles(self):
        a = Point(0, 0)
        b = Point(1, 0)
        c = Point(1, 1)
        line_ab, line_ba = Line(a, b), Line(b, a)
        line_ac, line_ca = Line(a, c), Line(c, a)
        angle_cab = Angle(line_ac, line_ab)
        angle_opposite = Angle(line_ca, line_ba)
        self.assertEqual(angle_opposite, angle_cab)