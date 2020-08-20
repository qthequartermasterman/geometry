from unittest import TestCase
from RadicalNumbers import Radical
import math
from fractions import Fraction


class TestRadical(TestCase):
    def setUp(self) -> None:
        self.index_radicand_list = [(1, 3),
                                    (2, 3),
                                    (3, 3),
                                    (2, 9),
                                    (2, 49),
                                    (2, 54),
                                    (2, 3, 2),
                                    (2, 3, -2),
                                    (3, 3375, 4),
                                    (1, 0, 3),
                                    (7, 23, -13),
                                    (2, Fraction('1/10'))]
        self.radical_dict = {pair: Radical(*pair) for pair in self.index_radicand_list}

    def test_init(self):
        index = 3
        radicand = 6
        coefficient = 7
        rad = Radical(index, radicand, coefficient)
        self.assertEqual(rad.index, index)
        self.assertEqual(rad.radicand, radicand)
        self.assertEqual(rad.coefficient, coefficient)

    def test_zero_index(self):
        with self.assertRaises(ValueError):
            Radical(0, 1, 2)

    def test_negative_radicand(self):
        with self.assertRaises(ValueError):
            Radical(2, -1, 2)

    def test_float(self):
        for pair, radical in self.radical_dict.items():
            if len(pair) == 2:
                expected_value = math.pow(pair[1], 1/pair[0])
            else:
                expected_value = pair[2] * math.pow(pair[1], 1/pair[0])
            self.assertEqual(float(radical), expected_value,
                             msg=f'Index: {pair[0]}, Radicand: {pair[1]}, Radical: {expected_value}')

    def test_abs(self):
        for _, value in self.radical_dict.items():
            self.assertEqual(abs(value).coefficient, abs(value.coefficient))

    def test_bool(self):
        # If a radical evaluates to false, then it is equal to zero, so we compare it to its float
        for _, value in self.radical_dict.items():
            self.assertEqual(bool(value), bool(float(value)))

    def test_neg(self):
        for _, value in self.radical_dict.items():
            self.assertEqual((-value).coefficient, -value.coefficient)

    def test_trunc(self):
        for _, value in self.radical_dict.items():
            self.assertEqual(value.__trunc__(), float(value).__trunc__())

    def test_mul(self):
        for _, radical in self.radical_dict.items():
            # multiply by an int
            ints = [3, 9, 1, 0, -2]
            for i in ints:
                new_radical: Radical = i * radical
                self.assertEqual(new_radical.coefficient, i * radical.coefficient)
                self.assertEqual(new_radical.radicand, radical.radicand)
                self.assertEqual(new_radical.index, radical.index)
            # multiply by a fraction
            fracs = [Fraction('1/10'), Fraction('3/2'), Fraction('-7'), Fraction('0'), Fraction('-4/5')]
            for f in fracs:
                new_radical: Radical = f * radical
                self.assertEqual(new_radical.coefficient, f * radical.coefficient)
                self.assertEqual(new_radical.radicand, radical.radicand)
                self.assertEqual(new_radical.index, radical.index)
            # multiply by a radical
            rads = self.radical_dict.values()
            for r in rads:
                new_radical: Radical = r * radical
                '''
                if r.index == radical.index:
                    self.assertEqual(new_radical.coefficient, radical.coefficient * r.coefficient)
                    self.assertEqual(new_radical.radicand, radical.radicand * r.radicand)
                    self.assertEqual(new_radical.index, radical.index)
                else:
                    self.assertEqual(new_radical.coefficient, radical.coefficient * r)
                    self.assertEqual(new_radical.radicand, radical.radicand)
                    self.assertEqual(new_radical.index, radical.index)
                '''
                # We will just multiply the floats and check if they're the same
                self.assertAlmostEqual(float(new_radical), float(r) * float(radical))

    def test_pow(self):
        for radical in self.radical_dict.values():
            for exponent in [0, 1, 2, 3, -2, -3]:
                exp_radical = radical**exponent
                if exponent == 0:
                    self.assertEqual(exp_radical, Radical(1, 1))
                else:
                    self.assertEqual(exp_radical.index, radical.index/exponent)