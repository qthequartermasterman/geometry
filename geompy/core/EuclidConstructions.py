"""This file contains various constructions found in Euclid's Elements"""
from geompy import Point, Construction
from geompy.core.Construction import ConstructionMode


def BaseConstruction(name='', construction_mode=ConstructionMode.DEFAULT):
    """A construction with two points a unit length apart.
    It is easier to use this function instead of instantiating manually one every time.
    """
    construction = Construction(name=name, construction_mode=construction_mode)
    a = Point(0, 0, 'A')
    b = Point(1, 0, 'B')
    construction.points = {a, b}
    construction.add_points_to_actions_update_queue({a, b})
    return construction


def EquilateralUnitTriangle():
    """Erect an equilateral triangle on a given segment."""
    # EuclidI1 requires both lines and circles, so set the ConstructionMode to default.
    construction = BaseConstruction(name='EuclidI1', construction_mode=ConstructionMode.DEFAULT)
    a, b = construction.points
    # The construction is to erect a triangle on the given segment, so this doesn't count as a step.
    construction.ab = construction.add_line(a, b, counts_as_step=False)
    construction.EuclidI1(construction.ab, Point(1, 1))  # Erect a triangle on the same side as Point(1,1)
    return construction


def RandomConstruction(length, construction_mode=ConstructionMode.DEFAULT):
    """Generates a random construction of given length. Not included in Euclid, but sometimes useful, nonetheless."""
    construction = BaseConstruction(name=f'RandomConstruction_{length}', construction_mode=construction_mode)
    construction.add_random_construction(length)
    return construction
