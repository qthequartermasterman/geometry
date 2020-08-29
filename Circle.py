from Point import Point
import matplotlib.pyplot as plt
from decimal import Decimal
from Object import Object


class Circle(Object):
    def __init__(self, center: Point, radius: Decimal = None, point2: Point = None, name=''):
        super().__init__()
        self.center = center
        self.dependencies.update(center.dependencies)
        if point2 is not None:
            self.point2 = point2
            self.radius = Decimal(abs(center-point2))
            self.name = name if name else f'c{center.name}r{center.name}{point2.name}'
            self.dependencies.update(point2.dependencies)
        else:
            self.point2 = None
            self.radius = Decimal(radius)
            self.name = name if name else f'c{center.name}r{radius}'

    def __repr__(self):
        return f'Circle {self.name} with center {self.center} and radius {self.radius:.2f}'

    def __hash__(self):
        return hash(repr(self))

    def plt_draw(self) -> plt.Circle:
        return plt.Circle((self.center.x, self.center.y), radius=self.radius, fill=False)
