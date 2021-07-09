from .Object import Object
from .Line import Line
from .Point import Point
from geompy.cas import equals
from math import acos


class Angle(Object):
    def __init__(self, line1: Line, line2: Line, vertex_point: Point):
        """
        Create a new angle. Note, the "interior" of the angle is oriented between the two rays pointing in the
        directions of line1's and line2's direction vectors.
        :param line1:
        :param line2:
        """
        super().__init__()
        self.line1 = line1
        self.line2 = line2
        self.vertex_point = vertex_point
        self.dependencies = {line1, line2}

    @property
    def measure(self):
        """Return the measure of the angle in radians."""
        return acos(float(self.line1.get_direction_vector() * self.line2.get_direction_vector()))

    def __eq__(self, other):
        return isinstance(other, Angle) and equals(self.measure, other.measure)

    def __repr__(self):
        return f'Angle {self.vertex_point} formed by lines {self.line1} and {self.line2}'
