"""This file contains various constructions found in Euclid's Elements"""

from .Point import Point
from .Construction import Construction


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


class BaseConstruction(Construction):
    """A construction with two points a unit length apart.
    It is easier to call this class instead of instantiating manually one every time.
    """
    def __init__(self):
        super().__init__()
        a = Point(0, 0, 'A')
        b = Point(1, 0, 'B')
        self.points = {a, b}
        self.actions = self.get_valid_actions({a, b}, True)