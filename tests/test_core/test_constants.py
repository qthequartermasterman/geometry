from unittest import TestCase
from symengine import sympify
import pickle


class GeometryTestCase(TestCase):
    def assertHashEqual(self, object1, object2, *args, **kwargs):
        return self.assertEqual(hash(object1), hash(object2), *args, **kwargs)

    def assertHashNotEqual(self, object1, object2, *args, **kwargs):
        return self.assertNotEqual(hash(object1), hash(object2), *args, **kwargs)

    def assertPickle(self, obj):
        object_bytes = pickle.dumps(obj)
        reconstructed = pickle.loads(object_bytes)
        return self.assertEqual(obj, reconstructed)


# Set of coordinates that should cover many useful test cases
coordinates = [(0, 0), (1, 0), (0, 1), (3, 2),
               ('1/2', 0), ('sqrt(3)', 1), ('exp(2)', '1/2'), ('-sqrt(3)', 'sqrt(1)')]


def evaluate(x):
    return sympify(x).evalf()
