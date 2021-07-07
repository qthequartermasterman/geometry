from unittest import TestCase

from geompy import Point, Line, Angle
from geompy.core.EuclidConstructions import (check_if_points_on_same_side, EquilateralUnitTriangle, BaseConstruction,
                                             EuclidI2, EuclidI3, RandomConstruction, EuclidI9, EuclidI10, Midpoint,
                                             PerpendicularBisector, EuclidI11, EuclidI12, ParallelLine, Perpendicular,
                                             DropPerpendicular, ErectPerpendicular)


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

    def test_EuclidI3(self):
        construction = BaseConstruction()
        a, b = construction.points
        c = construction.add_point(Point(10, 10, name='C'))
        short_line = construction.add_line(a, b)
        long_line = construction.add_line(a, c)
        shortened_line = EuclidI3(construction, short_line=short_line, long_line=long_line)
        self.assertEqual(abs(Line(a, b)), abs(shortened_line))

    def test_EuclidI9(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        c = construction.add_point(Point(1, 1, name='C'))
        line_ab = construction.add_line(a, b)
        line_ac = construction.add_line(a, c)
        angle_abc = Angle(line_ab, line_ac)
        line_bisecting_angle_abc = EuclidI9(construction, angle_abc)
        # Test if the line is the angle bisector by testing if the two sub angles are equal
        self.assertEqual(Angle(line_bisecting_angle_abc, line_ab), Angle(line_bisecting_angle_abc, line_ab))

    def test_EuclidI10(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        line_ab = construction.add_line(a, b)
        midpoint = EuclidI10(construction, line_ab)
        self.assertEqual(Point('1/2', 0), midpoint)
        midpoint = Midpoint(construction, line_ab)
        self.assertEqual(Point('1/2', 0), midpoint)

    def test_PerpendicularBisector(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        line_ab = construction.add_line(a, b)
        bisector = PerpendicularBisector(construction, line_ab)
        self.assertEqual(Line(Point('1/2',0), Point('1/2',1)), bisector)

    def test_ErectPerpendicular(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        line_ab = construction.add_line(a, b)
        bisector = EuclidI11(construction, line_ab, Point('1/2', 0))
        self.assertEqual(Line(Point('1/2', 0), Point('1/2', 1)), bisector)

    def test_ErectPerpendicularPointNotOnLineFails(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        c = construction.add_point(Point(1, 10, name='C'))
        self.assertRaises(ValueError, lambda: ErectPerpendicular(construction, Line(a,b), c))


    def test_DropPerpendicular(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        line_ab = construction.add_line(a, b)
        bisector = EuclidI12(construction, line_ab, Point('1/2', 1))
        self.assertEqual(Line(Point('1/2', 0), Point('1/2', 1)), bisector)

    def test_DropPerpendicularPointOnLineFails(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        c = construction.add_point(Point(0, 10, name='C'))
        self.assertRaises(ValueError, lambda: DropPerpendicular(construction, Line(a, b), c))

    def test_Perpendicular(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        c = construction.add_point(Point(1, 10, name='C'))
        perpendicular = Perpendicular(construction, Line(a,b), c)
        self.assertEqual(Line(Point(1,0), Point(1,10)), perpendicular)
        d = construction.add_point(Point(0, 10, name='D'))
        perpendicular = Perpendicular(construction, Line(a, b), d)
        self.assertEqual(Line(Point(0, 0), Point(0, 10)), perpendicular)

    def test_RandomConstruction(self):
        for i in range(5):
            construction = RandomConstruction(length=i)
            self.assertEqual(i, len(construction))

    def test_Parallel(self):
        construction = BaseConstruction()
        a = Point(1,1)
        parallel = ParallelLine(construction, Line(*construction.points), a)
        self.assertEqual(0, parallel.slope)
        self.assertEqual(1, parallel.intercept)
