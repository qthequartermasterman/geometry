import math
import matplotlib.pyplot as plt
# from decimal import Decimal
from Object import Object
import numpy as np
import sympy


class Point(Object):
    def __init__(self, x: sympy.core.expr.Expr, y: sympy.core.expr.Expr, name: str = ''):
        super().__init__()
        self.x = sympy.core.sympify(x)
        self.y = sympy.core.sympify(y)
        self.name = name
        #self.threshold = Decimal('1.0')**8

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
        if type(other) in (float, int, sympy.core.expr.Expr):  # Take the scalar Product
            return Point(other*self.x, other*self.y)
        elif type(other) is Point:  # Take the dot product
            return self.x*other.x + self.y*other.y
        else:
            print(f'invalid multiplication of {self} and {other}')
            raise NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __abs__(self):
        return sympy.sqrt(self * self)

    def __repr__(self):
        return f'Point {self.name}: ({self.x}, {self.y})'

    def __hash__(self):
        return hash((self.x, self.y))

    def plt_draw(self) -> plt.Circle:
        return plt.Circle((self.x, self.y), radius=0.02)

    def numpy(self) -> np.array:
        return np.array([self.x, self.y], dtype=np.float)

    def normalize(self):
        return abs(self)*self

p = Point(2,3)