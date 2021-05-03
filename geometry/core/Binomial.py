from numbers import Real
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
        for term in (self.left, self.right):
            if isinstance(term, Binomial):
                term.simplify()
            if isinstance(term, RadicalNumbers.Radical):
                term.simplify().eradicate_radicals()
        return self.left + self.right
        '''
        left = self.left
        right = self.right
        if isinstance(left, Binomial):
            left = self.left.simplify()
        if isinstance(right, Binomial):
            right = self.right.simplify()

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
            #raise NotImplementedError
            return
        '''

    def __add__(self, other):
        if isinstance(other, Binomial):
            radicals = self.get_radicals() + other.get_radicals()
            radicals = self.condense_radicals(radicals)
            radicals_nested_binomials = self.list_of_radicals_to_nested_binomial(radicals)
            fraction_part = self.get_fractions_integer() + other.get_fractions_integer()
        elif isinstance(other, RadicalNumbers.Radical):
            radicals = self.get_radicals()+[other]
            radicals = self.condense_radicals(radicals)
            radicals_nested_binomials = self.list_of_radicals_to_nested_binomial(radicals)
            fraction_part = self.get_fractions_integer()
        elif isinstance(other, (int, Fraction)):
            radicals = self.get_radicals()
            radicals = self.condense_radicals(radicals)
            radicals_nested_binomials = self.list_of_radicals_to_nested_binomial(radicals)
            fraction_part = self.get_fractions_integer() + other
        else:
            return NotImplemented

        if fraction_part:
            if radicals_nested_binomials:
                return Binomial(fraction_part, radicals_nested_binomials.simplify())
            else:
                return fraction_part
        else:
            return radicals_nested_binomials

    def __radd__(self, other):
        return self.__add__(other)

    def __neg__(self):
        return Binomial(-self.left, -self.right)

    def __pos__(self):
        return self

    def __mul__(self, other):
        # TODO: Fix issue where multiplying a binomial by itself doesn't simplify
        # test:
        # c = 3 + Radical(2,5)
        # c*c equals 9+(6+sqrt5)sqrt(5), but should equal 14 + 6sqrt5
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
        if self < 0:
            return -self
        else:
            return self

    def get_radicals(self):
        radicals = []

        for number in [self.left, self.right]:
            if isinstance(number, RadicalNumbers.Radical):
                simp = number.simplify().eradicate_radicals()
                if isinstance(simp, RadicalNumbers.Radical):
                    radicals.append(number)
            elif isinstance(number, Binomial):
                radicals += number.get_radicals()
            elif isinstance(number, (int, Fraction)):
                pass
            else:
                raise NotImplementedError

        return radicals

    def get_fractions_integer(self):
        rolling_fraction = Fraction('0')

        for number in [self.left, self.right]:
            if isinstance(number, (int, Fraction)):
                rolling_fraction += number
            elif isinstance(number, RadicalNumbers.Radical):
                simp = number.simplify().eradicate_radicals()
                if isinstance(simp, (int, Fraction)):
                    rolling_fraction += simp
            elif isinstance(number, Binomial):
                rolling_fraction += number.get_fractions_integer()
            else:
                raise NotImplementedError

        return rolling_fraction

    def condense_radicals(self, radicals=None):
        """
        We will first make a dictionary whose keys are (index, radicand) pairs. Each value is the rolling sum of
        radicals with that (index, radicand) pair. At the end, we return a list of of the condensed radicals.

        """
        if radicals is None:
            radicals = self.get_radicals()

        radicals_dict = {}
        for radical in radicals:
            simplified_radical = radical.simplify().eradicate_radicals()
            index_radicand = (simplified_radical.index, simplified_radical.radicand)
            if index_radicand in radicals_dict.keys():
                radicals_dict[index_radicand] += simplified_radical
            else:
                radicals_dict[index_radicand] = simplified_radical

        return list(radicals_dict.values())

    def list_of_radicals_to_nested_binomial(self, radicals=None):
        if radicals is None:
            radicals = self.condense_radicals()

        if len(radicals) > 1:
            return Binomial(radicals[0], self.list_of_radicals_to_nested_binomial(radicals[1:]))
        elif len(radicals) == 1:
            return radicals[0]
        else:
            return 0
