import copy

from .test_constants import GeometryTestCase

from geompy.core.Construction import Construction
from geompy.core.Point import Point
from geompy.core.Line import Line
from geompy.core.PrebuiltConstructions import BaseConstruction
from geompy.core.Angle import Angle
from geompy.cas import sympify

from copy import deepcopy


class TestConstruction(GeometryTestCase):
    def setUp(self) -> None:
        self.pointA = Point(0, 0)
        self.pointB = Point(1, 0)

        self.construction1 = Construction()
        self.construction1.add_point(self.pointA)
        self.construction1.add_point(self.pointB)

    def test_eq_same_construction(self):
        construction2 = deepcopy(self.construction1)
        self.assertEqual(self.construction1, construction2)
        self.assertHashEqual(self.construction1, construction2)

        construction2.add_line(self.pointA, self.pointB)
        construction2_copy = deepcopy(construction2)
        self.assertEqual(construction2, construction2_copy)
        self.assertHashEqual(construction2, construction2_copy)

        construction3 = deepcopy(self.construction1)
        construction3.add_circle(self.pointA, point2=self.pointB)
        construction3_copy = deepcopy(construction3)
        self.assertEqual(construction3, construction3_copy)
        self.assertHashEqual(construction3, construction3_copy)

        construction4 = deepcopy(self.construction1)
        construction4.add_circle(self.pointB, point2=self.pointA)
        construction4_copy = deepcopy(construction4)
        self.assertEqual(construction4, construction4_copy)
        self.assertHashEqual(construction4, construction4_copy)

    def test_eq_conjugate_constructions(self):
        # Conjugate constructions are constructions that are simply permutations of each other's steps.
        # They yield the same steps and the same points, but generate them in a different order
        construction2 = deepcopy(self.construction1)
        construction2.add_circle(self.pointA, point2=self.pointB)
        construction2.add_circle(self.pointB, point2=self.pointA)

        construction3 = deepcopy(self.construction1)
        construction3.add_circle(self.pointB, point2=self.pointA)
        construction3.add_circle(self.pointA, point2=self.pointB)

        self.assertEqual(construction2, construction3)
        self.assertHashEqual(construction2, construction3)

        construction2.add_line(self.pointA, self.pointB)
        construction3.add_line(self.pointB, self.pointA)

        self.assertEqual(construction2, construction3)
        self.assertHashEqual(construction2, construction3)

    def test_len(self):
        construction = deepcopy(self.construction1)
        self.assertEqual(len(construction), 0)
        construction.add_line(self.pointA, self.pointB)
        self.assertEqual(len(construction), 1)
        # Make sure adding duplicate does not effect length
        construction.add_line(self.pointA, self.pointB)
        self.assertEqual(len(construction), 1)

        # Add second step
        construction.add_circle(self.pointA, point2=self.pointB)
        self.assertEqual(len(construction), 2)

    def test_intersection_line_line_parallel(self):
        # two parallel lines should not give any intersections
        construction = deepcopy(self.construction1)
        line1 = construction.add_line(self.pointA, self.pointB)

        point_c = Point(0, 1)
        point_d = Point(1, 1)
        construction.add_point(point_c)
        construction.add_point(point_d)
        line2 = construction.add_line(point_c, point_d)

        point_e = Point(0, 10)
        point_f = Point(1, 10)
        construction.add_point(point_e)
        construction.add_point(point_f)
        line3 = construction.add_line(point_e, point_f)

        self.assertEqual(construction.update_intersections_with_object(line1), set())
        self.assertEqual(construction.update_intersections_with_object(line2), set())
        self.assertEqual(construction.update_intersections_with_object(line3), set())

    def test_intersection_line_line_intersecting(self):
        # two parallel lines should not give any intersections
        construction = deepcopy(self.construction1)
        line1 = construction.add_line(self.pointA, self.pointB)

        point_c = Point(2, 2)
        point_d = Point(1, 1)
        construction.add_point(point_c)
        construction.add_point(point_d)
        line2 = construction.add_line(point_c, point_d)
        self.assertEqual(construction.update_intersections_with_object(line2), {Point(0, 0)})

        point_e = Point(2, 2)
        point_f = Point(3, 1)
        construction.add_point(point_e)
        construction.add_point(point_f)
        line3 = construction.add_line(point_e, point_f)
        self.assertEqual(construction.update_intersections_with_object(line3), {Point(2, 2), Point(4, 0)})

    def test_intersection_circle_line_no_intersection(self):
        construction = self.construction1
        circle = construction.add_circle(self.pointA, self.pointB)

        point_c = Point(10, 0)
        point_d = Point(0, 10)
        line = construction.add_line(point_c, point_d)

        self.assertEqual(construction.update_intersections_with_object(line), set())
        self.assertEqual(construction.update_intersections_with_object(circle), set())

    def test_intersection_circle_line_tangent(self):
        construction = self.construction1
        circle = construction.add_circle(self.pointA, self.pointB)

        point_c = Point(0, 1)
        point_d = Point(1, 1)
        line = construction.add_line(point_c, point_d)

        self.assertEqual(construction.update_intersections_with_object(line), {Point(0, 1)})
        self.assertEqual(construction.update_intersections_with_object(circle), {Point(0, 1)})

    def test_intersection_circle_line_tangent2(self):
        construction = self.construction1
        # Circle with radius=2, so we can avoid using sqrts in this test
        circle = construction.add_circle(self.pointA, Point(1, 1))

        point_c = Point(0, 2)
        point_d = Point(2, 0)
        line = construction.add_line(point_c, point_d)
        print(construction.find_intersections(circle, line))

        self.assertEqual(construction.update_intersections_with_object(line), {Point(1, 1)})
        self.assertEqual(construction.update_intersections_with_object(circle), {Point(1, 1)})

    def test_intersection_circle_line_secant(self):
        construction = self.construction1
        # Circle with radius=2, so we can avoid using sqrts in this test
        circle = construction.add_circle(self.pointA, self.pointB)

        point_c = Point(0, 1)
        point_d = Point(1, 0)
        line = construction.add_line(point_c, point_d)

        self.assertEqual(construction.update_intersections_with_object(line), {Point(1, 0), Point(0, 1)})
        self.assertEqual(construction.update_intersections_with_object(circle), {Point(1, 0), Point(0, 1)})

    def test_check_if_points_on_same_side(self):
        a = Point(0, 0)
        b = Point(1, 0)
        c = Point(1, 1)
        d = Point(2, 2)
        e = Point(-1, -2)
        line1 = Line(a, b)
        self.assertTrue(Construction.check_if_points_on_same_side(line1, c, d))
        self.assertFalse(Construction.check_if_points_on_same_side(line1, c, e))

        line2 = Line(a, c)
        self.assertTrue(Construction.check_if_points_on_same_side(line2, b, e))

        self.assertRaises(ValueError, lambda: Construction.check_if_points_on_same_side(line1, a, c))

        line3 = Line(b, c)  # Vertical Line
        self.assertFalse(Construction.check_if_points_on_same_side(line3, d, e))
        self.assertTrue(Construction.check_if_points_on_same_side(line3, Point(10, 100), Point(10, 0)))

    def test_EuclidI2(self):
        construction = BaseConstruction()
        a, b = construction.points
        c = construction.add_point(Point(1, 1))
        new_line = construction.EuclidI2(Line(a, b), c)
        self.assertEqual(abs(Line(a, b)), abs(new_line))

    def test_EuclidI3(self):
        construction = BaseConstruction()
        a, b = construction.points
        c = construction.add_point(Point(10, 10, name='C'))
        short_line = construction.add_line(a, b)
        long_line = construction.add_line(a, c)
        shortened_line = construction.EuclidI3(short_line=short_line, long_line=long_line)
        self.assertEqual(abs(Line(a, b)), abs(shortened_line))

    def test_EuclidI10(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        line_ab = construction.add_line(a, b)
        midpoint = construction.EuclidI10(line_ab)
        self.assertEqual(Point('1/2', 0), midpoint)
        midpoint = construction.Midpoint(line_ab)
        self.assertEqual(Point('1/2', 0), midpoint)

    def test_PerpendicularBisector(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        line_ab = construction.add_line(a, b)
        bisector = construction.PerpendicularBisector(line_ab)
        self.assertEqual(Line(Point('1/2', 0), Point('1/2', 1)), bisector)

    def test_ErectPerpendicular(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        line_ab = construction.add_line(a, b)
        bisector = construction.EuclidI11(line_ab, Point('1/2', 0))
        self.assertEqual(Line(Point('1/2', 0), Point('1/2', 1)), bisector)

    def test_ErectPerpendicularPointNotOnLineFails(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        c = construction.add_point(Point(1, 10, name='C'))
        self.assertRaises(ValueError, lambda: construction.ErectPerpendicular(Line(a, b), c))

    def test_DropPerpendicular(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        line_ab = construction.add_line(a, b)
        bisector = construction.EuclidI12(line_ab, Point('1/2', 1))
        self.assertEqual(Line(Point('1/2', 0), Point('1/2', 1)), bisector)

    def test_DropPerpendicularPointOnLineFails(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        c = construction.add_point(Point(10, 0, name='C'))
        self.assertRaises(ValueError, lambda: construction.DropPerpendicular(Line(a, b), c))

    def test_Perpendicular(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        c = construction.add_point(Point(1, 10, name='C'))
        perpendicular = construction.Perpendicular(Line(a, b), c)
        self.assertEqual(Line(Point(1, 0), Point(1, 10)), perpendicular)
        d = construction.add_point(Point(0, 10, name='D'))
        perpendicular = construction.Perpendicular(Line(a, b), d)
        self.assertEqual(Line(Point(0, 0), Point(0, 10)), perpendicular)

    def test_Parallel(self):
        construction = BaseConstruction()
        a = Point(1, 1)
        parallel = construction.ParallelLine(Line(*construction.points), a)
        self.assertEqual(0, parallel.slope)
        self.assertEqual(1, parallel.intercept)

    def test_EuclidI9(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        c = construction.add_point(Point(1, 1, name='C'))
        line_ab = construction.add_line(a, b)
        line_ac = construction.add_line(a, c)
        angle_abc = Angle(line_ab, line_ac, a)
        line_bisecting_angle_abc = construction.EuclidI9(angle_abc)
        # Test if the line is the angle bisector by testing if the two sub angles are equal
        self.assertEqual(Angle(line_bisecting_angle_abc, line_ab, a), Angle(line_bisecting_angle_abc, line_ab, a))

    def test_Intersections_WeirdTypes_Fails(self):
        construction = BaseConstruction()
        a, b = construction.points
        line_ab = Line(a, b)
        self.assertRaises(NotImplementedError, lambda: construction.find_intersections(a, b))  # Two Points
        self.assertRaises(NotImplementedError, lambda: construction.find_intersections(2, 3))  # Two ints
        self.assertRaises(NotImplementedError, lambda: construction.find_intersections(a, 2))  # int and point
        self.assertRaises(NotImplementedError, lambda: construction.find_intersections(a, line_ab))  # line and point

    def test_intersect_circles_that_do_not_intersect(self):
        """Generate two circles that do NOT intersect. Should give an empty set as the intersections"""
        construction = Construction()
        a = construction.add_point(Point(0, 0))
        b = construction.add_point(Point(1, 0))
        c = construction.add_point(Point(5, 0))
        d = construction.add_point(Point(6, 0))
        circle_ab = construction.add_circle(center=a, point2=b)
        circle_cd = construction.add_circle(center=c, point2=d)
        intersections = construction.find_intersections_circle_circle(circle_ab, circle_cd)
        self.assertEqual(set(), intersections)

    def test_find_point(self):
        construction = BaseConstruction()
        # Point is in construction
        a = Point(0, 0)
        self.assertEqual(a, construction.find_point(a))
        # Point is not in construction
        c = Point(10, 10)
        self.assertEqual(None, construction.find_point(c))

    def test_check_lengths(self):
        construction = BaseConstruction()
        construction.add_point(Point(0, 1))
        construction.add_point(Point(1, 1))
        # Present lengths are 1 and sqrt(2).
        self.assertTrue(construction.check_lengths(1))
        self.assertTrue(construction.check_lengths(sympify('sqrt(2)')))
        # All other lengths should not be present
        self.assertFalse(construction.check_lengths(2))

    def test_get_present_lengths(self):
        construction = BaseConstruction()
        construction.add_point(Point(0, 1))
        construction.add_point(Point(1, 1))
        # There are only two present lengths, so the length of the dictionary should be 2
        self.assertEqual(2, len(construction.get_present_lengths()))

    def test_add_random_construction(self):
        for i in range(5):
            construction = BaseConstruction()
            construction.add_random_construction(i)
            self.assertEqual(i, len(construction))

    def test_update_valid_actions_no_force(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        # At first, we have only 3 valid actions.
        self.assertEqual(3, len(construction.actions))

        # Now we check if checking the actions at each step gives us the same as checking just at the end (Just in time)
        construction2 = copy.deepcopy(construction)
        # Add the line AB
        construction.add_line(*construction.points)
        construction2.add_line(*construction2.points)
        self.assertEqual(2, len(construction.actions))  # Only check the first construction
        # Circle A rAB
        construction.add_circle(center=a, point2=b)
        construction2.add_circle(center=a, point2=b)
        self.assertEqual(4, len(construction.actions))
        self.assertEqual(4, len(construction2.actions))


    def test_update_valid_actions_with_force(self):
        construction = BaseConstruction()
        a, b = construction.points
        if a.name != 'A':
            # Swap the points if we grabbed them backwards
            a, b = b, a
        # At first, we have only 3 valid actions.
        self.assertEqual(3, len(construction.update_valid_actions(force_calculate=True)))

        # Now we check if checking the actions at each step gives us the same as checking just at the end (Just in time)
        construction2 = copy.deepcopy(construction)
        # Add the line AB
        construction.add_line(*construction.points)
        construction2.add_line(*construction2.points)
        # Only check the first construction
        self.assertEqual(2, len(construction.update_valid_actions(force_calculate=True)))
        # Circle A rAB
        construction.add_circle(center=a, point2=b)
        construction2.add_circle(center=a, point2=b)
        self.assertEqual(4, len(construction.update_valid_actions(force_calculate=True)))
        self.assertEqual(4, len(construction2.update_valid_actions(force_calculate=True)))