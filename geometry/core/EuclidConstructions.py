"""This file contains various constructions found in Euclid's Elements"""

from geometry import Point, Construction, Line, Circle
from geometry.core.Construction import ConstructionMode
from geometry.cas import Infinity


def check_if_points_on_same_side(line: Line, point1: Point, point2: Point):
    if point1 in line or point2 in line:
        raise ValueError(f'At least one point {point1=} {point2=} is on {line=}')

    if line.slope == Infinity:
        point1_diff = point1.x - line.point1.x
        point2_diff = point2.x - line.point1.x
        # return (point1_diff > 0 and point2_diff > 0) or (point1_diff < 0 and point2_diff < 0)
        # Check if point1_diff and point2_diff have the same sign.
        return point1_diff * point2_diff > 0
    f_point1 = point1.y - line(point1.x)
    f_point2 = point2.y - line(point2.x)

    # Check if f_point1 and f_point2 have the same sign.
    return f_point1 * f_point2 > 0


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


def EquilateralUnitTriangle():
    """Erect an equilateral triangle on a given segment."""
    # EuclidI1 requires both lines and circles, so set the ConstructionMode to default.
    construction = BaseConstruction(name='EuclidI1',
                                    construction_mode=ConstructionMode.DEFAULT)
    a, b = construction.points
    # The construction is to erect a triangle on the given segment, so this doesn't count as a step.
    construction.ab = construction.add_line(a, b, counts_as_step=False)
    EuclidI1(construction, construction.ab, Point(1, 1))  # Erect a triangle on the same side as Point(1,1)
    return construction


def EuclidI1(construction: Construction, line: Line, side: Point, interesting=True) -> Point:
    """
    "To construct an equilateral triangle on a given finite straight line."
    Follows Euclid construction of an equilateral triangle on a line segment. Returns the third point of the triangle.

    An extra point is required to specify which side of the line to construct the triangle. Euclid takes for granted
    that it can be done on either side, and does so on the top, without loss of generality.

    :param construction:
    :param line:
    :param side:
    :param interesting: bool representing whether or not to mark subsequent steps as interesting.
    :return:
    """
    if side in line:
        raise ValueError(f'Point {side} is on line {line}, so side is ambiguous when erecting triangle.')
    if line not in construction.lines:
        raise ValueError(f'Cannot erect triangle. {line=} is not in {construction=}')

    a, b = line.point1, line.point2
    # These are the steps of the constructions
    circ1 = construction.add_circle(a, b)
    circ2 = construction.add_circle(b, a)
    intersections = construction.find_intersections(circ1, circ2)  # Only include circle intersections.
    c = None
    for intersect in intersections:
        if check_if_points_on_same_side(line, side, intersect):
            c = intersect
            construction.ac = construction.add_line(a, intersect, interesting=True)
            construction.bc = construction.add_line(b, intersect, interesting=True)
            break  # Only do it for one intersection point
    if c:
        return c
    else:
        raise ValueError(f'No intersections were on the same side of {line=} as point {side}')


def RandomConstruction(length, construction_mode=ConstructionMode.DEFAULT):
    """Generates a random construction of given length. Not included in Euclid, but sometimes useful, nonetheless."""
    construction = BaseConstruction(name=f'RandomConstruction_{length}', construction_mode=construction_mode)
    construction.add_random_construction(length)
    return construction
