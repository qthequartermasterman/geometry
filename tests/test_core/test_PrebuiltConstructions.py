from unittest import TestCase

from geompy import Point
from geompy.core.PrebuiltConstructions import (EquilateralUnitTriangle, BaseConstruction, RandomConstruction)


class Test(TestCase):

    def test_equilateral_triangle(self):
        """This will test that the equilateral unit triangle is created properly. Additionally will test EuclidI1"""
        construction = EquilateralUnitTriangle()
        self.assertTrue(Point('1/2', 'sqrt(3)/2') in construction.points)
        self.assertFalse(Point('1/2', '-sqrt(3)/2') not in construction.points)

    def test_RandomConstruction(self):
        for i in range(5):
            construction = RandomConstruction(length=i)
            self.assertEqual(i, len(construction))

    def test_BaseConstruction(self):
        construction = BaseConstruction()
        self.assertEqual({Point(0, 0), Point(1, 0)}, construction.points)
        construction_with_name = BaseConstruction(name='NamedBaseConstruction')
        self.assertEqual({Point(0, 0), Point(1, 0)}, construction_with_name.points)
        self.assertEqual('NamedBaseConstruction', construction_with_name.name)
