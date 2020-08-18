import math
import matplotlib.pyplot as plt
from decimal import Decimal


class Point:
    def __init__(self, x: float, y: float, name: str = ''):
        self.x = Decimal(x)
        self.y = Decimal(y)
        self.name = name

    def __eq__(self, other):
        #return self.x == other.x and self.y == other.y
        #return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)
        return self.x.quantize(Decimal('1.0')**16) == other.x.quantize(Decimal('1.0')**16) and \
               self.y.quantize(Decimal('1.0')**16) == other.y.quantize(Decimal('1.0')**16)

    def __sub__(self, other):
        return Point(self.x-other.x, self.y-other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        if type(other) in (float, int, Decimal):  # Take the scalar Product
            return Point(other*self.x, other*self.y)
        elif type(other) is Point:  # Take the dot product
            return self.x*other.x + self.y*other.y
        else:
            print(f'invalid multiplication of {self} and {other}')
            raise NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __abs__(self):
        return Decimal.sqrt(self * self)

    def __repr__(self):
        return f'Point {self.name}: ({self.x:.4f}, {self.y:.4f})'

    def __hash__(self):
        #return hash(repr(self))
        return hash((self.x.quantize(Decimal('1.0')**16), self.y.quantize(Decimal('1.0')**16)))

    def plt_draw(self) -> plt.Circle:
        return plt.Circle((self.x, self.y), radius=0.05)
