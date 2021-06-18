"""This file contains various constructions found in Euclid's Elements"""

from geometry import Point
from geometry import Construction
from geometry.core.Construction import ConstructionMode


class EuclidI1(Construction):
    """Erect an equilateral triangle on a given segment."""
    def __init__(self):
        super().__init__(name='EuclidI1')
        a = Point(0, 0, 'A')
        b = Point(1, 0, 'B')
        self.a = a
        self.b = b
        self.c: Point
        self.points.update({a, b})
        self.interesting_points.update({a, b})  # Mark these as interesting

        # The construction is to erect a triangle on the given segment, so this doesn't count as a step.
        self.ab = self.add_line(a, b, counts_as_step=False)

        # These are the steps of the constructions
        self.circ1 = self.add_circle(a, b)
        self.circ2 = self.add_circle(b, a)
        intersections = self.points - {a, b}
        for intersect in intersections:
            self.c = intersect
            self.ac = self.add_line(a, intersect, interesting=True)
            self.bc = self.add_line(b, intersect, interesting=True)
            break  # Only do it for one intersection point


class RandomConstruction(Construction):
    """Generates a random construction of given length. Not included in Euclid, but sometimes useful, nonetheless."""
    def __init__(self, length):
        super(RandomConstruction, self).__init__(name=f'RandomConstruction_{length}')
        a = Point(0, 0, 'A')
        b = Point(1, 0, 'B')
        self.a = a
        self.b = b
        self.add_point(a, True)
        self.add_point(b, True)
        self.add_random_construction(length)


def BaseConstruction(name='', construction_mode=ConstructionMode.DEFAULT):
    """A construction with two points a unit length apart.
    It is easier to use this function instead of instantiating manually one every time.
    """
    construction = Construction(name=name, construction_mode=construction_mode)
    a = Point(0, 0, 'A')
    b = Point(1, 0, 'B')
    construction.points = {a, b}
    construction.actions = construction.get_valid_actions({a, b}, True)
    return construction
