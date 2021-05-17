import matplotlib.pyplot as plt
import numpy as np
from symengine import Expr, sqrt, sympify
from .Object import Object
from .utils import symengine_equality, optimized_simplify, Expression, is_nan


class Point(Object):
    def __init__(self, x: Expression, y: Expression, name: str = ''):
        super().__init__()
        # self.x = sympy.core.sympify(x).simplify()
        # self.y = sympy.core.sympify(y).simplify()
        if is_nan(x) or is_nan(y):
            raise TypeError(f'Coordinates are NaN: {x},\t {y}')
        self.x = optimized_simplify(sympify(x))
        self.y = optimized_simplify(sympify(y))
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Point):
            #return self.x == other.x and self.y == other.y
            return symengine_equality(self.x, other.x) and symengine_equality(self.y, other.y)
        else:
            return False

    def __sub__(self, other):
        return Point(self.x-other.x, self.y-other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        if isinstance(other, Point):  # Take the dot product
            return self.x*other.x + self.y*other.y
        else:  # If the other object is not a point, then take a scalar product
            return Point(other * self.x, other * self.y)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __abs__(self):
        return sqrt(self * self)

    def __repr__(self):
        return f'Point {self.name}: ({self.x}, {self.y})'

    def __hash__(self):
        return hash((self.x, self.y))

    def plt_draw(self) -> plt.Circle:
        return plt.Circle((self.x.evalf(), self.y.evalf()), radius=0.02)

    def numpy(self) -> np.array:
        return np.array([self.x, self.y], dtype=np.float32)

    def normalize(self):
        return (1/abs(self))*self

    def __getstate__(self):
        """

        :return:
        """
        state = self.__dict__.copy()
        # Change the unpickleable entries to sympy objects (which are pickleable)
        state['x'] = repr(state['x'])
        state['y'] = repr(state['y'])
        return state

    def __setstate__(self, state):
        """

        :param state:
        :return:
        """
        self.__dict__.update(state)
        self.x = sympify(self.x)
        self.y = sympify(self.y)

    def simplify(self):
        return Point(x=self.x.simplify(), y=self.y.simplify(), name=self.name)