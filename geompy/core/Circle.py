import numpy as np

from .Object import Object
from .Point import Point, FastPoint
from geompy.cas import (equals as symengine_equality,
                        simplify as optimized_simplify,
                        Expression,
                        sympify)

from symengine import Expr, Number


class Circle(Object):
    def __init__(self, center: Point, radius: Expression = None, point2: Point = None, name='', pre_simplified=False):
        super().__init__()
        self.center = center
        self.dependencies.update(center.dependencies)
        self._simplified = pre_simplified
        if point2 is not None:
            self.point2 = point2
            self.radius = optimized_simplify(abs(center - point2))
            self.name = name if name else f'c{center.name}r{center.name}{point2.name}'
            self.dependencies.update(point2.dependencies)
        else:
            self.point2 = None
            self.radius = optimized_simplify(sympify(radius))
            self.name = name if name else f'c{center.name}r{radius}'

        if self.center == self.point2 or radius == 0:
            raise ValueError(f'Circle cannot have radius of 0: {self.center, self.point2, self.radius, self.name}')

    def __repr__(self):
        """String repr of the circle"""
        return f'Circle {self.name} with center {self.center} and radius {self.radius}'

    def __hash__(self):
        """Circles are equivalent if their centers are equal and their radii are equal"""
        return hash((self.center, self.radius))

    def __eq__(self, other):
        """Circles are equivalent if their centers are equal and their radii are equal"""
        return isinstance(other, Circle) and self.center == other.center and self.radius == other.radius

    def __contains__(self, item) -> bool:
        """
        A point is in the circle if it satisfies the equation
        :param item:
        :return: bool. True if point is on the circle
        """
        return isinstance(item, Point) and symengine_equality(abs(item - self.center), self.radius)

    def __getstate__(self):
        """

        :return:
        """
        state = self.__dict__.copy()
        # Change the unpickleable entries to sympy objects (which are pickleable)
        # state['radius'] = sympy.core.sympify(state['radius'])
        state['radius'] = repr(state['radius'])
        return state

    def __setstate__(self, state):
        """

        :param state:
        :return:
        """
        self.__dict__.update(state)
        self.radius = sympify(self.radius)

    def simplify(self):
        if self._simplified:
            return self
        else:
            c = Circle(center=self.center.simplify(), radius=self.radius.simplify(), name=self.name,
                       pre_simplified=True)
            c.dependencies = self.dependencies
            return c


class FastCircle(Object):
    def __init__(self, center: FastPoint, radius: Expression = None, point2: Point = None, name='', pre_simplified=False):
        super().__init__()
        self.center = center
        self.dependencies.update(center.dependencies)
        self._simplified = pre_simplified
        if point2 is not None:
            self.point2 = point2
            self.radius = optimized_simplify(abs(center - point2))
            self.name = name if name else f'c{center.name}r{center.name}{point2.name}'
            self.dependencies.update(point2.dependencies)
        else:
            self.point2 = None
            if isinstance(radius, Expr) or isinstance(radius, Number):
                radius = optimized_simplify(radius)
                radius = radius.evalf()
            self.radius = np.float64(radius)
            self.name = name if name else f'c{center.name}r{radius}'

        if self.center == self.point2 or radius == 0:
            raise ValueError(f'Circle cannot have radius of 0: {self.center, self.point2, self.radius, self.name}')

    def __hash__(self):
        """Circles are equivalent if their centers are equal and their radii are equal"""
        return hash((self.center, float(self.radius)))

    def __eq__(self, other):
        """Circles are equivalent if their centers are equal and their radii are equal"""
        return isinstance(other, FastCircle) and self.center == other.center \
               and np.allclose(np.array(self.radius, dtype=float), np.array(other.radius, dtype=float))

    def __getstate__(self):
        """

        :return:
        """
        state = self.__dict__.copy()
        # Change the unpickleable entries to sympy objects (which are pickleable)
        # state['radius'] = sympy.core.sympify(state['radius'])
        # state['radius'] = repr(state['radius'])
        return state

    def __setstate__(self, state):
        """

        :param state:
        :return:
        """
        self.__dict__.update(state)
        # self.radius = sympify(self.radius)

    def __contains__(self, item):
        return np.allclose(np.array(abs(item - self.center), dtype=float), np.array(self.radius, dtype=float))

    def __repr__(self):
        """String repr of the circle"""
        return f'Circle {self.name} with center {self.center} and radius {self.radius}'
