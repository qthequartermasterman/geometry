from .Object import Object
from .Point import Point

import matplotlib.pyplot as plt
import sympy


class Circle(Object):
    def __init__(self, center: Point, radius: sympy.core.expr.Expr = None, point2: Point = None, name=''):
        super().__init__()
        self.center = center
        self.dependencies.update(center.dependencies)
        if point2 is not None:
            self.point2 = point2
            self.radius = abs(center - point2)
            self.name = name if name else f'c{center.name}r{center.name}{point2.name}'
            self.dependencies.update(point2.dependencies)
        else:
            self.point2 = None
            self.radius = sympy.core.sympify(radius)
            self.name = name if name else f'c{center.name}r{radius}'

    def __repr__(self):
        """String repr of the circle"""
        return f'Circle {self.name} with center {self.center} and radius {self.radius}'

    def __hash__(self):
        """Circles are equivalent if their centers are equal and their radii are equal"""
        return hash((self.center, self.radius))

    def __eq__(self, other):
        """Circles are equivalent if their centers are equal and their radii are equal"""
        return isinstance(other, Circle) and self.center == other.center and self.radius.equals(other.radius)

    def __contains__(self, item) -> bool:
        """
        A point is in the circle if it satisfies the equation
        :param item:
        :return: bool. True if point is on the circle
        """
        return isinstance(item, Point) and abs(item-self.center) == self.radius

    def plt_draw(self) -> plt.Circle:
        """
        :return: plt.Circle representing a matplotlib pyplot circle representing our circle.
        """
        return plt.Circle((self.center.x.evalf(), self.center.y.evalf()),
                          radius=self.radius.evalf(), fill=False)
