"""This file contains various constructions found in Euclid's Elements"""

from geometry import Point
from geometry import Construction
from geometry.core.Construction import ConstructionMode





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


def EuclidI1():
    """Erect an equilateral triangle on a given segment."""
    construction = BaseConstruction(name='EuclidI1', construction_mode=ConstructionMode.DEFAULT)  # EuclidI1 requires both lines and circles
    a, b = construction.points
    # The construction is to erect a triangle on the given segment, so this doesn't count as a step.
    construction.ab = construction.add_line(a, b, counts_as_step=False)

    # These are the steps of the constructions
    construction.circ1 = construction.add_circle(a, b)
    construction.circ2 = construction.add_circle(b, a)
    intersections = {point for point in construction.points if point.y != 0}  # Only include circle intersections.
    for intersect in intersections:
        construction.c = intersect
        construction.ac = construction.add_line(a, intersect, interesting=True)
        construction.bc = construction.add_line(b, intersect, interesting=True)
        break  # Only do it for one intersection point
    return construction


def RandomConstruction(length, construction_mode=ConstructionMode.DEFAULT):
    """Generates a random construction of given length. Not included in Euclid, but sometimes useful, nonetheless."""
    construction = BaseConstruction(name=f'RandomConstruction_{length}', construction_mode=construction_mode)
    construction.add_random_construction(length)
    return construction
