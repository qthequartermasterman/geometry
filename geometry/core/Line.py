import matplotlib.pyplot as plt

from .Object import Object
from .Point import Point

from geometry.cas import (Expr,
                          sympify,
                          Infinity,
                          equals as symengine_equality,
                          simplify as optimized_simplify,
                          Expression)

from methodtools import lru_cache
import pickle
import numpy as np


class Line(Object):
    def __init__(self, point1: Point, point2: Point, name='', slope: Expression = None, intercept: Expression = None,
                 pre_simplified=False):
        """
        Lines represent the set of points that can be drawn by tracing a straightedge between two points.
        :param point1: Point representing the first defining point.
        :param point2: Point representing the second defining point.
        :param name: optional string representing the name of the Line
        """
        super().__init__()
        if slope is None and intercept is None:
            self.point1 = point1
            self.point2 = point2
            self.dependencies.update(point1.dependencies | point2.dependencies)
            self.slope = self.calculate_slope(point1, point2)
            self.intercept = self.calculate_intercept(point1, point2, self.slope)
        else:
            self.slope = slope
            self.intercept = intercept
            self.point1 = Point(0, intercept)
            self.point2 = Point(1, slope + intercept)
        # self.name = name if name else u'\u0305'.join(f'{point1.name}{point2.name} ')
        self.name = name if name else f'{point1.name}{point2.name}'
        self._simplified = pre_simplified

    @staticmethod
    @lru_cache(maxsize=None)
    def calculate_slope(point1: Point, point2: Point) -> Expr:
        """
        Calculate the slope of a given line, as if embedded onto the cartesian plane. This is the $m$ in $y=mx+b$.
        Slope is calculated with the change in y divided by change in x. Since we are using sympy, we can safely get
        exact values without worrying about floating point errors.
        :param point1: Point representing the first defining point.
        :param point2: Point representing the second defining point.
        :return: sympy expression representing the slope between two points.
        """
        if not point1.x == point2.x:
            try:
                slope = (point2.y - point1.y) / (point2.x - point1.x)
                return optimized_simplify(slope)
            except ZeroDivisionError:
                # If the line is vertical, its slope is undefined or "infinite"
                return Infinity
        return Infinity

    # def calculate_intercept(self, point1: Point, point2: Point, slope: sympy.core.expr.Expr = None):
    @staticmethod
    @lru_cache(maxsize=None)
    def calculate_intercept(point1: Point, point2: Point, slope: Expression = None):
        """
        Calculate the y-intercept of a line. This is the $b$ in $y=mx+b$.
        :param point1: Point representing the first defining point.
        :param point2: Point representing the second defining point.
        :param slope: optional sympy expression representing the slope of the line
        :return: sympy expression representing the slope between two points.
        """
        if slope is None:
            # slope is unknown.
            slope = Line.calculate_slope(point1, point2)
        if slope == Infinity:
            # Line is vertical
            return Infinity
        else:
            slope = slope
        return optimized_simplify(point1.y - point1.x * slope)  # Solve for y-intercept.

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
            if self.slope == Infinity and other.slope == Infinity:
                # Both Lines are vertical, check the x-coordinate
                return self.point1.x == other.point1.x
            else:
                # If one or both of the lines are not vertical, check to make sure they have the same
                # slope and intercept.
                return symengine_equality(self.slope, other.slope) and \
                       symengine_equality(self.intercept, other.intercept)
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

        if self.slope != Infinity:
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
            # 1. Check if defining Point
            # 2. Check if slope is infinity and x-coordinates match (vertical line)
            # 3. Check if satisfies equation
            return (item in (self.point1, self.point2)) \
                   or (self.slope == Infinity and item.x == self.point1.x) \
                   or symengine_equality(item.x * self.slope + self.intercept, item.y)
        else:
            return False

    def plt_draw(self) -> plt.Line2D:
        """

        :return: plt.Line2D representing a matplotlib pyplot line representing our Line.
        """
        return plt.Line2D((self.point1.x.evalf(), self.point2.x.evalf()),
                          (self.point1.y.evalf(), self.point2.y.evalf()))

    def __getstate__(self):
        """

        :return:
        """
        state = self.__dict__.copy()
        # Change the unpickleable entries to sympy objects (which are pickleable)
        state['point1'] = pickle.dumps(state['point1'])
        state['point2'] = pickle.dumps(state['point2'])
        # state['slope'] = sympy.core.sympify(state['slope'])
        # state['intercept'] = sympy.core.sympify(state['intercept'])
        state['slope'] = repr(state['slope'])
        state['intercept'] = repr(state['intercept'])
        return state

    def __setstate__(self, state):
        """

        :param state:
        :return:
        """
        self.__dict__.update(state)
        self.point1 = pickle.loads(self.point1)
        self.point2 = pickle.loads(self.point2)
        self.slope = sympify(self.slope)
        self.intercept = sympify(self.intercept)

    def simplify(self):
        if self._simplified:
            return self
        else:
            l = Line(self.point1.simplify(), self.point2.simplify(), name=self.name, pre_simplified=True)
            l.dependencies = self.dependencies
            return l

    def calculate_value_at_x(self, x) -> Expression:
        if self.slope is not Infinity:
            return self.slope * x + self.intercept
        else:
            raise ValueError('Cannot use vertical line as a mathematical function. Output is all real numbers or none.')

    def __call__(self, x) -> Expression:
        return self.calculate_value_at_x(x)

    def get_perpendicular_at_point(self, point: Point):
        if self.slope == 0:
            return Line(point, point + Point(0, 1))
        new_slope = -1 / self.slope
        new_intercept = (self.slope - new_slope) * point.x + self.intercept
        return Line(point, point, slope=new_slope, intercept=new_intercept)

    def get_direction_vector(self):
        return (self.point2 - self.point1).normalize()


class FastLine(Line):
    def __getstate__(self):
        """

        :return:
        """
        state = self.__dict__.copy()
        # Change the unpickleable entries to sympy objects (which are pickleable)
        state['point1'] = pickle.dumps(state['point1'])
        state['point2'] = pickle.dumps(state['point2'])
        return state

    def __setstate__(self, state):
        """

        :param state:
        :return:
        """
        self.__dict__.update(state)
        self.point1 = pickle.loads(self.point1)
        self.point2 = pickle.loads(self.point2)

    @lru_cache()
    @staticmethod
    def calculate_slope(point1: Point, point2: Point) -> float:
        """
        Calculate the slope of a given line, as if embedded onto the cartesian plane. This is the $m$ in $y=mx+b$.
        Slope is calculated with the change in y divided by change in x. Since we are using sympy, we can safely get
        exact values without worrying about floating point errors.
        :param point1: Point representing the first defining point.
        :param point2: Point representing the second defining point.
        :return: float representing the slope between two points.
        """
        if not symengine_equality(point1.x, point2.x):
            try:
                slope = (point2.y - point1.y) / (point2.x - point1.x)
                return slope
            except ZeroDivisionError:
                # If the line is vertical, its slope is undefined or "infinite"
                return Infinity
        return Infinity

    @lru_cache()
    @staticmethod
    def calculate_intercept(point1: Point, point2: Point, slope: float = None):
        """
        Calculate the y-intercept of a line. This is the $b$ in $y=mx+b$.
        :param point1: Point representing the first defining point.
        :param point2: Point representing the second defining point.
        :param slope: optional float representing the slope of the line
        :return: float representing the slope between two points.
        """
        if slope is None:
            # slope is unknown.
            slope = FastLine.calculate_slope(point1, point2)
        if slope == Infinity:
            # Line is vertical
            return Infinity
        else:
            slope = slope
        return point1.y - point1.x * slope  # Solve for y-intercept.

    def __contains__(self, item) -> bool:
        """
        Determines if the other point is included in the line.
        :param item: the other point
        :return: bool. True if point is on line.
        """
        if isinstance(item, Point):
            # If the item is a generating point or if it satisfies the equation, then it is indeed in the line.
            # 1. Check if defining Point
            # 2. Check if slope is infinity and x-coordinates match (vertical line)
            # 3. Check if satisfies equation
            return (item in (self.point1, self.point2)) \
                   or (self.slope == Infinity and item.x == self.point1.x) \
                   or (self.slope != Infinity and np.isclose(
                np.array(item.x * self.slope + self.intercept, dtype=float),
                np.array(item.y, dtype=float)))
        else:
            return False

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
        if isinstance(other, FastLine):
            if self.slope == Infinity and other.slope == Infinity:
                # Both Lines are vertical, check the x-coordinate
                return self.point1.x == other.point1.x
            else:
                # If one or both of the lines are not vertical, check to make sure they have the same
                # slope and intercept.
                return symengine_equality(self.slope, other.slope) and \
                       symengine_equality(self.intercept, other.intercept)
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

        if self.slope != Infinity:
            # return hash((self.slope.data.tobytes(), self.intercept.data.tobytes()))
            return hash((self.slope, self.intercept))
        else:
            # return hash((self.slope.data.tobytes(), self.intercept.data.tobytes(), self.point1.x))
            return hash((self.slope, self.intercept, self.point1.x))
