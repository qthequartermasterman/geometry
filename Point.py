import math
import matplotlib.pyplot as plt
from decimal import Decimal
from Object import Object


class Point(Object):
    def __init__(self, x: float, y: float, name: str = ''):
        super().__init__()
        self.x = Decimal(x)
        self.y = Decimal(y)
        self.name = name
        self.threshold = Decimal('1.0')**8


    def __eq__(self, other):
        #return self.x == other.x and self.y == other.y
        #return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)
        threshold = self.threshold
        if isinstance(other, Point):
            return self.x.quantize(threshold) == other.x.quantize(threshold) and self.y.quantize(threshold) == other.y.quantize(threshold)
        else:
            return False

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
        threshold = self.threshold
        return hash((self.x.quantize(threshold), self.y.quantize(threshold)))

    def plt_draw(self) -> plt.Circle:
        return plt.Circle((self.x, self.y), radius=0.02)
