from Point import Point
import matplotlib.pyplot as plt
from decimal import Decimal


class Circle:
    def __init__(self, center: Point, radius: Decimal = None, point2: Point = None, name=''):
        self.center = center
        if point2 is not None:
            self.point2 = point2
            self.radius = Decimal(abs(center-point2))
            self.name = name if name else f'c{center.name}r{center.name}{point2.name}'
        else:
            self.point2 = None
            self.radius = Decimal(radius)
            self.name = name if name else f'c{center.name}r{radius}'

    def __repr__(self):
        return f'Circle {self.name} with center {self.center} and radius {self.radius}'

    def __hash__(self):
        return hash(repr(self))

    def plt_draw(self) -> plt.Circle:
        return plt.Circle((self.center.x, self.center.y), radius=self.radius, fill=False)
