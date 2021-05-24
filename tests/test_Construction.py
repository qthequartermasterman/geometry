from test_constants import GeometryTestCase

from geometry.core.Construction import Construction
from geometry.core.Point import Point
from geometry.core.Line import Line
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

        pointC = Point(0, 1)
        pointD = Point(1, 1)
        construction.add_point(pointC)
        construction.add_point(pointD)
        line2 = construction.add_line(pointC, pointD)

        pointE = Point(0, 10)
        pointF = Point(1, 10)
        construction.add_point(pointE)
        construction.add_point(pointF)
        line3 = construction.add_line(pointE, pointF)

        self.assertEqual(construction.update_intersections_with_object(line1), set())
        self.assertEqual(construction.update_intersections_with_object(line2), set())
        self.assertEqual(construction.update_intersections_with_object(line3), set())

    def test_intersection_line_line_intersecting(self):
        # two parallel lines should not give any intersections
        construction = deepcopy(self.construction1)
        line1 = construction.add_line(self.pointA, self.pointB)

        pointC = Point(2, 2)
        pointD = Point(1, 1)
        construction.add_point(pointC)
        construction.add_point(pointD)
        line2 = construction.add_line(pointC, pointD)
        self.assertEqual(construction.update_intersections_with_object(line2), {Point(0, 0)})

        pointE = Point(2, 2)
        pointF = Point(3, 1)
        construction.add_point(pointE)
        construction.add_point(pointF)
        line3 = construction.add_line(pointE, pointF)
        self.assertEqual(construction.update_intersections_with_object(line3), {Point(2, 2), Point(4, 0)})

    def test_intersection_circle_line_no_intersection(self):
        construction = self.construction1
        circle = construction.add_circle(self.pointA, self.pointB)

        pointC = Point(10, 0)
        pointD = Point(0, 10)
        line = construction.add_line(pointC, pointD)

        self.assertEqual(construction.update_intersections_with_object(line), set())
        self.assertEqual(construction.update_intersections_with_object(circle), set())

    def test_intersection_circle_line_tangent(self):
        construction = self.construction1
        circle = construction.add_circle(self.pointA, self.pointB)

        pointC = Point(0, 1)
        pointD = Point(1, 1)
        line = construction.add_line(pointC, pointD)

        self.assertEqual(construction.update_intersections_with_object(line), {Point(0, 1)})
        self.assertEqual(construction.update_intersections_with_object(circle), {Point(0, 1)})

    def test_intersection_circle_line_tangent2(self):
        construction = self.construction1
        # Circle with radius=2, so we can avoid using sqrts in this test
        circle = construction.add_circle(self.pointA, Point(1, 1))

        pointC = Point(0, 2)
        pointD = Point(2, 0)
        line = construction.add_line(pointC, pointD)
        print(construction.find_intersections(circle, line))

        self.assertEqual(construction.update_intersections_with_object(line), {Point(1, 1)})
        self.assertEqual(construction.update_intersections_with_object(circle), {Point(1, 1)})

    def test_intersection_circle_line_secant(self):
        construction = self.construction1
        # Circle with radius=2, so we can avoid using sqrts in this test
        circle = construction.add_circle(self.pointA, self.pointB)

        pointC = Point(0, 1)
        pointD = Point(1, 0)
        line = construction.add_line(pointC, pointD)

        self.assertEqual(construction.update_intersections_with_object(line), {Point(1, 0), Point(0,1)})
        self.assertEqual(construction.update_intersections_with_object(circle), {Point(1, 0), Point(0,1)})
