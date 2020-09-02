"""This file contains various constructions found in Euclid's Elements"""

from Construction import Construction
from Point import Point


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

        # The construction is to erect a triangle on the given segment, so this doesn't count as a step.
        self.ab = self.add_line(a, b, counts_as_step=False)

        # These are the steps of the constructions
        self.circ1 = self.add_circle(a, b)
        self.circ2 = self.add_circle(b, a)
        intersections = self.points - {a, b}
        for intersect in intersections:
            self.c = intersect
            self.ac = self.add_line(a, intersect)
            self.bc = self.add_line(b, intersect)
            break  # Only do it for one intersection point


class RandomConstruction(Construction):
    """Generates a random construction of given length. Not included in Euclid, but sometimes useful, nonetheless."""
    def __init__(self, length):
        super(RandomConstruction, self).__init__(name=f'RandomConstruction_{length}')
        a = Point(0, 0, 'A')
        b = Point(1, 0, 'B')
        self.a = a
        self.b = b
        self.points.update({a, b})
        self.add_random_construction(length)
