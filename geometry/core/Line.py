import matplotlib.pyplot as plt
import sympy
from .Object import Object
from .Point import Point


class Line(Object):
    def __init__(self, point1: Point, point2: Point, name=''):
        """
        Lines represent the set of points that can be drawn by tracing a straightedge between two points.
        :param point1: Point representing the first defining point.
        :param point2: Point representing the second defining point.
        :param name: optional string representing the name of the Line
        """
        super().__init__()
        self.point1 = point1
        self.point2 = point2
        self.dependencies.update(point1.dependencies | point2.dependencies)
        self.slope = self.calculate_slope(point1, point2)
        self.intercept = self.calculate_intercept(point1, point2, self.slope)
        # self.name = name if name else u'\u0305'.join(f'{point1.name}{point2.name} ')
        self.name = name if name else f'{point1.name}{point2.name}'

    @staticmethod
    def calculate_slope(point1: Point, point2: Point) -> sympy.core.expr.Expr:
        """
        Calculate the slope of a given line, as if embedded onto the cartesian plane. This is the $m$ in $y=mx+b$.
        Slope is calculated with the change in y divided by change in x. Since we are using sympy, we can safely get
        exact values without worrying about floating point errors.
        :param point1: Point representing the first defining point.
        :param point2: Point representing the second defining point.
        :return: sympy expression representing the slope between two points.
        """
        if not point1.x.equals(point2.x):
            try:
                slope = (point2.y - point1.y) / (point2.x - point1.x)
                return slope
            except ZeroDivisionError:
                # If the line is vertical, its slope is undefined or "infinite"
                return sympy.core.numbers.Infinity()
        return sympy.core.numbers.Infinity()

    def calculate_intercept(self, point1: Point, point2: Point, slope: sympy.core.expr.Expr = None):
        """
        Calculate the y-intercept of a line. This is the $b$ in $y=mx+b$.
        :param point1: Point representing the first defining point.
        :param point2: Point representing the second defining point.
        :param slope: optional sympy expression representing the slope of the line
        :return: sympy expression representing the slope between two points.
        """
        if slope == sympy.core.numbers.Infinity():
            # Line is vertical
            return sympy.core.numbers.Infinity()
        elif slope is None:
            # slope is unknown.
            slope = self.calculate_slope(point1, point2)
        else:
            slope = slope
        return point1.y - point1.x * slope  # Solve for y-intercept.

    def __repr__(self) -> str:
        """
        :return: a string that contains all the information describing the line.
        """
        return f'Line {self.name} through {self.point1} and {self.point2}: y={self.slope}x+{self.intercept}'

    def __eq__(self, other) -> bool:
        """
        Equality of lines is defined by having the same slope and intercept. If either defer, then they are unequal.
        Note: Two lines can have differing generating points and still be equal, as long as you pick points on the same
        line.

        In the case of vertical lines, which have undefined slope and intercept, they are equal if they have the same
        x-coordinates.

        :param other: the other line
        :return: bool. True if equal, else false.
        """
        if isinstance(other, Line):
            if self.slope != sympy.core.numbers.Infinity():  # Line is not vertical
                return self.slope == other.slope and self.intercept == other.intercept
            else:  # Line is vertical
                if self.point1.x == other.point1.x:
                    return True
        else:  # Not the same type. Equality is not supported.
            return False

    def __hash__(self) -> int:
        """
        Return a unique hash for each line.
        These three pieces of information uniquely define a line:
        There is a 1-1 correspondence between lines and (slope, intercept) pairs EXCEPT for vertical lines
        there is a 1-1 correspondence between vertical lines and the x-coordinate of any point on them
        :return: hash encoding all the data necessary to uniquely describe a line.
        """

        if self.slope != sympy.core.numbers.Infinity():
            return hash((self.slope, self.intercept))
        else:
            return hash((self.slope, self.intercept, self.point1.x))

    def __abs__(self) -> float:
        """
        This returns the length of the line segment between the two defining points
        :returns: float representing the euclidean distance between the two defining points.
        """
        return abs(self.point2 - self.point1)

    def __contains__(self, item) -> bool:
        """
        Determines if the other point is included in the line.
        :param item: the other point
        :return: bool. True if point is on line.
        """
        if isinstance(item, Point):
            # If the item is a generating point or if it satisfies the equation, then it is indeed in the line.
            return (item in (self.point1, self.point2)) or (item.x * self.slope + self.intercept == item.y)
        else:
            return False

    def plt_draw(self) -> plt.Line2D:
        """

        :return: plt.Line2D representing a matplotlib pyplot line representing our Line.
        """
        return plt.Line2D((self.point1.x.evalf(), self.point2.x.evalf()),
                          (self.point1.y.evalf(), self.point2.y.evalf()))
