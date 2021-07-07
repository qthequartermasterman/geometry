"""This file contains various constructions found in Euclid's Elements"""
from geompy import Point, Construction, Line, Angle
from geompy.core.Construction import ConstructionMode
from geompy.cas import Infinity


def check_if_points_on_same_side(line: Line, point1: Point, point2: Point):
    if point1 in line or point2 in line:
        raise ValueError(f'At least one point {point1} {point2} is on {line}')

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


def pick_point_on_side(line: Line, side: Point, points: {Point}, same_side=True):
    for intersect in points:
        if same_side:
            if check_if_points_on_same_side(line, side, intersect):
                return intersect
        else:
            if not check_if_points_on_same_side(line, side, intersect):
                return intersect
    else:
        raise ValueError(f'No points were on the same side of {line} as point {side}')


def pick_point_not_on_line(line: Line):
    """Pick a point not on the line for when we do not care about which side."""
    return line.point1 + line.get_perpendicular_at_point(line.point1).get_direction_vector()


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
        raise ValueError(f'Cannot erect triangle. {line} is not in {construction}')

    a, b = line.point1, line.point2
    # These are the steps of the constructions
    circ1 = construction.add_circle(a, b, interesting=interesting)
    circ2 = construction.add_circle(b, a, interesting=interesting)
    intersections = construction.find_intersections(circ1, circ2)  # Only include circle intersections.
    c = None
    for intersect in intersections:
        if check_if_points_on_same_side(line, side, intersect):
            c = intersect
            construction.ac = construction.add_line(a, intersect, interesting=interesting)
            construction.bc = construction.add_line(b, intersect, interesting=interesting)
            break  # Only do it for one intersection point
    if c:
        return c
    else:
        raise ValueError(f'No intersections were on the same side of {line} as point {side}')


def EuclidI2(construction: Construction, line_segment: Line, a: Point, interesting=True) -> Line:
    """
    To copy a segment.
    :param construction:
    :param line_segment:
    :param a:
    :param interesting:
    :return:
    """
    if a not in construction.points:
        raise ValueError(f'Cannot copy line segment. Point {a} not in {construction}.')
    # Choose b,c as the ends of the linesegments.
    b, c = line_segment.point1, line_segment.point2
    # Occasionally, we can accidentally choose b = a.
    # Without loss of generality, choose b != a.
    if a == b:
        b, c = c, b
    ab = construction.add_line(a, b, interesting=interesting)

    d = EuclidI1(construction, ab, pick_point_not_on_line(ab))
    circle_bc = construction.add_circle(b, c, interesting=interesting)
    intersections = construction.find_intersections_line_circle(Line(d, b), circle_bc)
    g = pick_point_on_side(line_segment, d, intersections, same_side=False)
    circle_dg = construction.add_circle(d, g, interesting=interesting)
    intersections = construction.find_intersections_line_circle(Line(d, a), circle_dg)
    final_point = pick_point_on_side(ab, d, intersections, same_side=False)
    return construction.add_line(a, final_point, interesting=interesting)


def EuclidI3(construction: Construction, short_line: Line, long_line: Line, interesting=True) -> Line:
    """
    To cut off a segment.
    :param construction:
    :param short_line:
    :param long_line:
    :param interesting:
    :return:
    """
    if short_line not in construction.lines or long_line not in construction.lines:
        raise ValueError(f'Cannot cut off line segment. {short_line} or {long_line} not in {construction}')
    a, b = long_line.point1, long_line.point2
    line_ad = EuclidI2(construction, short_line, a, interesting=interesting)
    d = line_ad.point2
    circle_def = construction.add_circle(center=a, point2=d, interesting=interesting)
    intersections = construction.find_intersections_line_circle(long_line, circle_def)
    e = pick_point_on_side(Line(a, d), b, intersections)
    return Line(a, e)


def EuclidI9(construction: Construction, angle: Angle, interesting=True) -> Line:
    """
    To bisect an angle.
    :param construction:
    :param angle:
    :param interesting:
    :return:
    """
    a = angle.vertex_point
    line1, line2 = angle.line1, angle.line2
    d = line1.point1 if line1.point1 != a else line1.point2  # pick an arbitrary point on line1 that is not a.
    # Cut off point E from line2 with length AD
    e = EuclidI3(construction, short_line=Line(a, d), long_line=line2, interesting=interesting).point2
    # We need to pick a point opposite DE from A to show which side to erect the equilateral triangle.
    # Start at D, and walk in the direction of D-A.
    side = 2 * d - a
    line_de = construction.add_line(d, e, interesting=interesting)
    f = EuclidI1(construction, line_de, side, interesting=interesting)
    return construction.add_line(a, f, interesting=interesting)


def EuclidI10(construction: Construction, line: Line, interesting=True) -> Point:
    """
    To bisect a given finite straight line.

    NOTE: This construction is included in here as written in Elements for completion sake. Erecting a triangle and
    then bisecting the angle is effective, but slow when drawing every step. Use the perpendicular bisector instead.
    This construction is given first to make the proof easier.
    :param construction:
    :param line:
    :param interesting:
    :return:
    """
    a, b = line.point1, line.point2
    side = pick_point_not_on_line(line)  # We don't care which side to erect the triangle.
    c = EuclidI1(construction, line, side, interesting=interesting)
    angle = Angle(Line(c, b), Line(c, a))
    perp_bisector = EuclidI9(construction, angle, interesting=interesting)
    (intersections,) = construction.find_intersections_line_line(line, perp_bisector)
    return intersections

def PerpendicularBisector(construction: Construction, line: Line, interesting=True) -> Line:
    """
    Erect the perpendicular bisector of a given line much faster.
    :param construction:
    :param line:
    :param interesting:
    :return:
    """
    a, b = line.point1, line.point2
    # These are the steps of the constructions
    circ1 = construction.add_circle(a, b, interesting=interesting)
    circ2 = construction.add_circle(b, a, interesting=interesting)
    intersections = construction.find_intersections(circ1, circ2)  # Only include circle intersections.
    return construction.add_line(*intersections, interesting=interesting)


def RandomConstruction(length, construction_mode=ConstructionMode.DEFAULT):
    """Generates a random construction of given length. Not included in Euclid, but sometimes useful, nonetheless."""
    construction = BaseConstruction(name=f'RandomConstruction_{length}', construction_mode=construction_mode)
    construction.add_random_construction(length)
    return construction
