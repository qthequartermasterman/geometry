from numbers import Real
import math


class Radical(Real):
    def __init__(self, index, radicand, coefficient=1):
        if index == 0:
            raise ValueError('Radical Index cannot be 0')
        if radicand < 0:
            raise ValueError('Radicand cannot be negative')
        self.index = index
        self.radicand = radicand
        self.coefficient = coefficient

    @staticmethod
    def is_square(x):
        return x == math.isqrt(x)**2

    def __abs__(self):
        return Radical(self.index, self.radicand, abs(self.coefficient))

    def __add__(self, other):
        pass

    def __bool__(self):
        # If either the coefficient or the radicand are zero, it evaluates to zero
        return bool(self.coefficient) and bool(self.radicand)

    def __ceil__(self):
        return math.ceil(float(self))

    def __divmod__(self, other):
        pass

    def __eq__(self, other):
        return math.isclose(float(self), float(other))

    def __float__(self):
        return float(self.coefficient) * float(float(self.radicand) ** (1 / self.index))

    def __floor__(self):
        return math.floor(float(self))

    def __floordiv__(self, other):
        return float(self).__floordiv__(other)

    def __le__(self, other) -> bool:
        pass

    def __lt__(self, other):
        pass

    def __mod__(self, other):
        pass

    def __mul__(self, other):
        if isinstance(other, Radical):
            if other.index == self.index:
                new_coefficient = self.coefficient * other.coefficient
                new_radicand = self.radicand * other.radicand
                return Radical(self.index, new_radicand, new_coefficient)
            else:
                # TODO: Use lcm as new index instead of product
                common_index = self.index*other.index
                new_radicand = self.radicand**(common_index/self.index) * other.radicand**(common_index/other.index)
                new_coefficient = self.coefficient * other.coefficient
                return Radical(common_index, new_radicand, new_coefficient)
        else:
            new_coefficient = self.coefficient * other
            return Radical(self.index, self.radicand, new_coefficient)

    def __pow__(self, exponent):
        if exponent == 0:
            return Radical(1, 1)  # Anything to the 0-th power is 1
        else:
            return Radical(self.index/exponent, self.radicand, self.coefficient**exponent)

    def __radd__(self, other):
        pass

    def __rfloordiv__(self, other):
        pass

    def __rmod__(self, other):
        pass

    def __rmul__(self, other):
        return self.__mul__(other)

    def __round__(self, n=None):
        pass

    def __rpow__(self, base):
        raise NotImplemented

    def __rsub__(self, other):
        pass

    def __rtruediv__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __truediv__(self, other):
        pass

    def __trunc__(self):
        return float(self).__trunc__()

    def __neg__(self):
        return Radical(self.index, self.radicand, -self.coefficient)

    def __pos__(self):
        pass

    def __repr__(self):
        coef = str(self.coefficient) if self.coefficient != 1 else ''
        if self.index == 1:
            return f'{coef}({self.radicand})'
        elif self.index == 2:
            return f'{coef}√({self.radicand})'
        elif self.index == 3:
            return f'{coef}\u221B({self.radicand})'
        elif self.index == 4:
            return f'{coef}\u221C({self.radicand})'
        else:
            return f'{coef}({self.radicand})^(1/{self.index})'
