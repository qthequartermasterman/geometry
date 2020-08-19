from Point import Point
import math
import matplotlib.pyplot as plt
from decimal import Decimal


class Line:
    def __init__(self, point1: Point, point2: Point, name=''):
        self.point1 = point1
        self.point2 = point2
        self.slope = self.calculate_slope(point1, point2)
        self.intercept = self.calculate_intercept(point1, point2, self.slope)
        #self.name = name if name else u'\u0305'.join(f'{point1.name}{point2.name} ')
        self.name = name if name else f'{point1.name}{point2.name}'

    @staticmethod
    def calculate_slope(point1: Point, point2: Point):
        if point1.x.quantize(Decimal('.1')**8) != point2.x.quantize(Decimal('.1')**8):
            try:
                slope = Decimal(point2.y-point1.y)/Decimal(point2.x-point1.x)
                return slope.quantize(Decimal(10)**-12)
            except ZeroDivisionError:  # If the line is vertical, its slope is undefined or "infinite"
                return Decimal('Infinity')
        return Decimal('Infinity')

    def calculate_intercept(self, point1: Point, point2: Point, slope=None):
        if slope == Decimal('Infinity'):
            return Decimal('Infinity')
        elif slope is None:
            slope = self.calculate_slope(point1, point2)
        else:
            slope = slope
        return point1.y - point1.x * slope

    def __repr__(self):
        return f'Line {self.name} through {self.point1} and {self.point2}, with equation: y={self.slope:.2f}x+{self.intercept:.2f}'

    def __hash__(self):
        return hash(repr(self))

    def __abs__(self):
        """This returns the length of the line segment between the two defining points"""
        return abs(self.point2-self.point1)

    def plt_draw(self) -> plt.Line2D:
        return plt.Line2D((self.point1.x, self.point2.x), (self.point1.y, self.point2.y))