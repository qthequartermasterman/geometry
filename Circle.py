from Point import Point
import matplotlib.pyplot as plt
from Object import Object
import sympy


class Circle(Object):
    def __init__(self, center: Point, radius: sympy.core.expr.Expr = None, point2: Point = None, name=''):
        super().__init__()
        self.center = center
        self.dependencies.update(center.dependencies)
        if point2 is not None:
            self.point2 = point2
            self.radius = abs(center-point2)
            self.name = name if name else f'c{center.name}r{center.name}{point2.name}'
            self.dependencies.update(point2.dependencies)
        else:
            self.point2 = None
            self.radius = sympy.core.sympify(radius)
            self.name = name if name else f'c{center.name}r{radius}'

    def __repr__(self):
        return f'Circle {self.name} with center {self.center} and radius {self.radius}'

    def __hash__(self):
        return hash(repr(self))

    def plt_draw(self) -> plt.Circle:
        return plt.Circle((self.center.x.evalf(), self.center.y.evalf()),
                          radius=self.radius.evalf(), fill=False)
