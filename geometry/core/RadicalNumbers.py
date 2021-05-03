from numbers import Real
import math
from fractions import Fraction
from geometry.core.Binomial import Binomial


class Radical(Real):
    def __init__(self, index, radicand, coefficient=1):
        if index == 0:
            raise ValueError('Radical Index cannot be 0')
        if not (isinstance(index, int) or isinstance(index, Fraction)):
            raise TypeError('Radical Index must be int or Fraction')
        if radicand < 0:
            raise ValueError('Radicand cannot be negative')
        self.index = Fraction(index)
        self.radicand = radicand
        self.coefficient = coefficient

    def __abs__(self):
        return Radical(self.index, self.radicand, abs(self.coefficient))

    def __add__(self, other):
        self_simp = self.simplify()
        if isinstance(other, (Radical, Binomial)):  # If the other object is simplifiable, let's simplify it.
            other = other.simplify()
        if isinstance(self_simp.eradicate_radicals(), (Fraction, int)):
            # If self is not really a radical, then addition works totally differently
            return self_simp.eradicate_radicals() + other

        else:  # self is a radical
            if isinstance(other, Radical):
                if self_simp.index == other.index and self_simp.radicand == other.radicand:
                    new_rad = Radical(self_simp.index, self_simp.radicand, self_simp.coefficient + other.coefficient)
                    return new_rad.simplify().eradicate_radicals()
                else:
                    return Binomial(self, other)
            elif isinstance(other, (int, Fraction)):
                return Binomial(other, self)  # Put the radical second
            else:
                return NotImplemented

    def __bool__(self):
        # If either the coefficient or the radicand are zero, it evaluates to zero
        return bool(self.coefficient) and bool(self.radicand)

    def __ceil__(self):
        return math.ceil(float(self))

    def __divmod__(self, other):
        # This is a slow implementation. But it works fine.
        return self.__floordiv__(other), self.__mod__(other)

    def __eq__(self, other):
        # Simplifying both radicals to test for equality is expensive... But it's definitely correct.
        # This could probably be made cheaper by saving the result of simplify() as an instance variable
        self_simp = self.simplify()
        if isinstance(other, Radical):
            other_simp = other.simplify()
            return self_simp.get_tuple() == other_simp.get_tuple()
        elif isinstance(other, Fraction) or isinstance(other, int):
            return self_simp.eradicate_radicals() == other
        else:
            return NotImplemented

    def __float__(self):
        return float(self.coefficient) * float(float(self.radicand) ** (1 / self.index))

    def __floor__(self):
        return math.floor(float(self))

    def __floordiv__(self, other):
        return float(self).__floordiv__(other)

    def __hash__(self):
        # I adapted this hash algorithm from fractions.Fraction
        # All numbers should have the same hash, regardless of representation.
        # This is more difficult than it seems.
        simplified = self.simplify()
        if simplified.radicand == 1:
            # Get integers right.
            return hash(simplified.eradicate_radicals())
            # Expensive check, but definitely correct.
        if simplified == float(simplified):
            return hash(float(simplified))
        else:
            # Use tuple's hash to avoid a high collision rate on
            # simple fractions.
            return hash(simplified.get_tuple())

    def __le__(self, other) -> bool:
        return float(self) <= float(other)

    def __lt__(self, other):
        return float(self) < float(other)

    def __mod__(self, other):
        return self - self.__floordiv__(other)

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
        elif isinstance(other, Binomial):
            return Binomial(other.left*self.simplify().eradicate_radicals(), other.right*self.simplify().eradicate_radicals())
        else:
            new_coefficient = self.coefficient * other
            return Radical(self.index, self.radicand, new_coefficient)

    def __pow__(self, exponent):
        if exponent == 0:
            return Radical(1, 1, self.coefficient)  # Anything to the 0-th power is 1
        else:
            return Radical(Fraction(self.index)/Fraction(exponent), self.radicand, self.coefficient**exponent)

    def __radd__(self, other):
        return self.__add__(other)

    def __rfloordiv__(self, other):
        pass

    def __rmod__(self, other):
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __round__(self, n=None):
        return round(float(self), n)

    def __rpow__(self, base):
        # In general, this is a transcendental number. I don't want to get into that right now.
        return NotImplemented

    def __rsub__(self, other):
        return other + -self

    def __rtruediv__(self, other):
        if isinstance(other, Radical):
            if other.index == self.index:
                coefficient = Fraction(other.coefficient) / self.coefficient
                radicand = other.radicand / self.radicand
                return Radical(self.index, radicand, coefficient)
            else:
                # TODO: Use lcm as new index instead of product
                common_index = self.index * other.index
                new_radicand = other.radicand ** (common_index / other.index) / self.radicand ** (common_index / self.index)
                new_coefficient = Fraction(other.coefficient) / self.coefficient
                return Radical(common_index, new_radicand, new_coefficient)
        elif isinstance(other, (int, Fraction)):
            coefficient = Fraction(other) / self.coefficient
            return Radical(self.index, self.radicand, coefficient)
        else:
            return NotImplemented

    def __sub__(self, other):
        return self + (-other)

    def __truediv__(self, other):
        if isinstance(other, Radical):
            if other.index == self.index:
                coefficient = Fraction(self.coefficient)/other.coefficient
                radicand = self.radicand/other.radicand
                return Radical(self.index, radicand, coefficient)
            else:
                # TODO: Use lcm as new index instead of product
                common_index = self.index * other.index
                new_radicand = self.radicand ** (common_index / self.index) / other.radicand ** (
                            common_index / other.index)
                new_coefficient = Fraction(self.coefficient) / other.coefficient
                return Radical(common_index, new_radicand, new_coefficient)
        elif isinstance(other, (int, Fraction)):
            coefficient = Fraction(self.coefficient) / other
            return Radical(self.index, self.radicand, coefficient)
        else:
            return NotImplemented

    def __trunc__(self):
        return float(self).__trunc__()

    def __neg__(self):
        return Radical(self.index, self.radicand, -self.coefficient)

    def __pos__(self):
        return self

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

    def simplify(self):
        # Find squares/cubes/etc... inside of the radical-> move to coefficient
        # If the index is an improper fraction, divide it out and move the extras to the coefficient
        index = self.index
        rolling_radicand = self.radicand
        rolling_coefficient = self.coefficient

        if isinstance(index, Fraction) and index.denominator > index.numerator:
            quotient, remainder = divmod(index.denominator, index.numerator)
            index = Fraction(index.numerator)/Fraction(remainder)
            rolling_coefficient *= rolling_radicand**quotient

        if isinstance(self.radicand, int):
            for n in range(2, self.radicand):
                quotient, remainder = divmod(rolling_radicand, n**index)
                while remainder == 0:
                    rolling_radicand = quotient
                    rolling_coefficient *= n
                    quotient, remainder = divmod(rolling_radicand, n ** index)
                if n > rolling_radicand:
                    break
            return Radical(index, rolling_radicand, rolling_coefficient)
        elif isinstance(self.radicand, Fraction):
            rolling_coefficient = Fraction(rolling_coefficient)
            rolling_coef_numerator = rolling_coefficient.numerator
            rolling_rad_numerator = rolling_radicand.numerator
            rolling_coef_denominator = rolling_coefficient.denominator
            rolling_rad_denominator = rolling_radicand.denominator
            for n in range(2, rolling_rad_numerator):
                quotient, remainder = divmod(rolling_rad_numerator, n**index)
                while remainder == 0:
                    rolling_rad_numerator = quotient
                    rolling_coef_numerator *= n
                    quotient, remainder = divmod(rolling_rad_numerator, n ** index)
            for n in range(2, rolling_rad_denominator):
                quotient, remainder = divmod(rolling_rad_denominator, n**index)
                while remainder == 0:
                    rolling_rad_denominator = quotient
                    rolling_coef_denominator *= n
                    quotient, remainder = divmod(rolling_rad_denominator, n ** index)
            rolling_coefficient = Fraction(rolling_coef_numerator)/Fraction(rolling_coef_denominator)
            rolling_radicand = Fraction(rolling_rad_numerator)/Fraction(rolling_rad_denominator)
            return Radical(index, rolling_radicand, rolling_coefficient)
        else:
            raise NotImplementedError

    def eradicate_radicals(self):
        """Eradicates radicals whose radicand is 1"""
        if self.radicand == 1:
            return self.coefficient
        elif self.radicand == 0 or self.coefficient == 0:
            return 0
        else:
            return self

    def get_tuple(self):
        return self.index, self.radicand, self.coefficient


def sqrt(radicand, coefficient=1):
    return Radical(2, radicand, coefficient)
