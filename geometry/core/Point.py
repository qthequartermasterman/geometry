import matplotlib.pyplot as plt
import numpy as np
import sympy
from .Object import Object


class Point(Object):
    def __init__(self, x: sympy.core.expr.Expr, y: sympy.core.expr.Expr, name: str = ''):
        super().__init__()
        # self.x = sympy.core.sympify(x).simplify()
        # self.y = sympy.core.sympify(y).simplify()
        self.x = sympy.core.sympify(x)
        self.y = sympy.core.sympify(y)
        self.name = name

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x.equals(other.x) and self.y.equals(other.y)
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
        return sympy.sqrt(self * self)

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
