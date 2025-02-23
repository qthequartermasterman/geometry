import numpy as np
from .Object import Object
from geompy.cas import Expr

from geompy.cas import (sqrt,
                        sympify,
                        equals,
                        simplify,
                        Expression,
                        is_nan)


class Point(Object):
    def __init__(self, x: Expression, y: Expression, name: str = '', pre_simplified=False):
        super().__init__()
        # self.x = sympy.core.sympify(x).simplify()
        # self.y = sympy.core.sympify(y).simplify()
        if is_nan(x) or is_nan(y):
            raise TypeError(f'Point Coordinates are NaN: ({x},\t {y}), with dependencies {self.dependencies}')
        self.x = simplify(sympify(x))
        self.y = simplify(sympify(y))
        self.name = name
        self._simplified = pre_simplified

    def __eq__(self, other):
        if isinstance(other, Point):
            return equals(self.x, other.x) and equals(self.y, other.y)
        else:
            return False

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        if isinstance(other, Point):  # Take the dot product
            return self.x * other.x + self.y * other.y
        else:  # If the other object is not a point, then take a scalar product
            return Point(other * self.x, other * self.y)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __abs__(self):
        return simplify(sqrt(self * self))

    def __repr__(self):
        return f'Point {self.name}: ({self.x}, {self.y})'

    def __hash__(self):
        return hash((self.x, self.y))

    def numpy(self) -> np.array:
        return np.array([self.x, self.y], dtype=np.float32)

    def normalize(self):
        return (1 / abs(self)) * self

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
        if self._simplified:
            return self
        else:
            p = Point(x=self.x.simplify(), y=self.y.simplify(), name=self.name, pre_simplified=True)
            p.dependencies = self.dependencies
            return p


class FastPoint(Object):
    def __init__(self, x: Expression = None, y: Expression = None, array: np.ndarray = None, name: str = ''):
        super().__init__()
        self.name = name
        if isinstance(array, np.ndarray):
            if array.shape == (2,):
                self.array = array
            else:
                raise ValueError(
                    f'If instantiating Fast Point using array, it must have shape (2,). Array has shape {array}')
        else:
            if x is None or y is None:
                raise TypeError(f'Fast Points must be instantiated with either an array or both an x and y coordinate')
            if isinstance(x, str):
                x = sympify(x)
            if isinstance(y, str):
                y = sympify(y)
            if isinstance(x, Expr):
                x = x.evalf()
            if isinstance(y, Expr):
                y = y.evalf()
            self.array = np.array([x, y], dtype=np.float32)

    def __eq__(self, other):
        if isinstance(other, FastPoint):
            return np.allclose(self.array, other.array)
        else:
            return False

    def __sub__(self, other):
        diff_array = self.array - other.array
        return FastPoint(array=diff_array)

    def __add__(self, other):
        sum_array = self.array + other.array
        return FastPoint(array=sum_array)

    def __mul__(self, other):
        if isinstance(other, FastPoint):  # Take the dot product
            return self.array.dot(other.array)
        else:  # If the other object is not a point, then take a scalar product
            prod_array = other * self.array
            return FastPoint(array=prod_array)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __abs__(self):
        # Norm/Magnitude of the vector. Equivalent to the sqrt of the dot product with itself.
        return np.sqrt(self.array.dot(self.array))

    def __repr__(self):
        return f'Point {self.name}: ({self.array[0]}, {self.array[1]})'

    def __hash__(self):
        # We cannot hash an ndarray direectly, so instead hash the underlying data as bytes
        array = np.array(self.array, dtype=np.float16)
        return hash(array.data.tobytes())

    def numpy(self) -> np.array:
        return self.array

    def normalize(self):
        array = self.array / abs(self)
        return FastPoint(array=array)

    def simplify(self):
        return self

    @property
    def x(self):
        return self.array[0]

    @property
    def y(self):
        return self.array[1]
