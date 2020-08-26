from abc import abstractmethod
from numbers import Real
from typing import overload
import math
from fractions import Fraction
import RadicalNumbers


class Binomial(Real):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __float__(self) -> float:
        return float(self.left) + float(self.right)

    def __trunc__(self) -> int:
        return float(self).__trunc__()

    def __floor__(self) -> int:
        return math.floor(float(self))

    def __ceil__(self) -> int:
        return math.ceil(float(self))

    def __round__(self, ndigits: None = ...):
        return round(float(self), ndigits)

    def __floordiv__(self, other):
        return NotImplemented

    def __rfloordiv__(self, other):
        return NotImplemented

    def __mod__(self, other):
        return NotImplemented

    def __rmod__(self, other):
        return NotImplemented

    def __lt__(self, other) -> bool:
        return float(self) < float(other)

    def __le__(self, other) -> bool:
        return float(self) <= float(other)

    def __eq__(self, other):
        self_simp = self.simplify()
        if isinstance(other, Binomial):
            other = other.simplify()
            if isinstance(other, Binomial):
                return (self_simp.left == other.left and self_simp.right == other.right) or (self_simp.right == other.left and self_simp.left == other.right)
        else:
            return NotImplemented

    def __hash__(self):
        # I adapted this hash algorithm from fractions.Fraction
        # All numbers should have the same hash, regardless of representation.
        # This is more difficult than it seems.
        simplified = self.simplify()
        if isinstance(simplified, Binomial):
            return hash(frozenset([self.left, self.right]))
        if simplified == float(simplified):
            return hash(float(simplified))
        else:
            return hash(simplified)

    def __repr__(self):
        return f'{self.left} + {self.right}'

    def simplify(self):
        left = self.left
        right = self.right
        if isinstance(left, type(right)):
            return left + right
        if (isinstance(left, int) and isinstance(right, Fraction)) or \
                (isinstance(right, int) and isinstance(left, Fraction)):
            return left + right
        if isinstance(left, RadicalNumbers.Radical) and isinstance(right, (int, Fraction)):
            return Binomial(right, left)  # Put the radical second
        if isinstance(left, (Fraction, int)) and isinstance(right, RadicalNumbers.Radical):
            return self
        else:
            raise NotImplementedError

    def __add__(self, other):
        if isinstance(other, Binomial):
            return NotImplemented
        elif isinstance(other, RadicalNumbers.Radical):
            return NotImplemented
        elif isinstance(other, (int, Fraction)):
            return NotImplemented
        else:
            return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __neg__(self):
        return Binomial(-self.left, -self.right)

    def __pos__(self):
        return self

    def __mul__(self, other):
        return self.left * other + self.right * other  # If addition is implemented properly, this distribution law should hold

    def __rmul__(self, other):
        # Multiplication is commutative over the reals
        return self.__mul__(other)

    def __div__(self, other):
        return NotImplemented

    def __rdiv__(self, other):
        return NotImplemented

    def __truediv__(self, other):
        return NotImplemented

    def __rtruediv__(self, other):
        return NotImplemented

    def __pow__(self, exponent):
        return NotImplemented

    def __rpow__(self, base):
        return base**self.left * base**self.right

    def __abs__(self):
        # The absolute value of a binomial is curiously nontrivial...
        raise NotImplementedError