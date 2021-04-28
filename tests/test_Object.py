from unittest import TestCase
from Object import Object

class TestObject(TestCase):
    def test_set_dependencies_general(self):
        dependencies = {1, 2, 3}
        object = Object()
        object.set_dependencies(dependencies)
        self.assertEqual(object.dependencies, dependencies)

    def test_set_dependencies_object(self):
        object1 = Object()
        object2 = Object()
        object3 = Object()
        obj1_dep = {object2, object3}
        obj2_dep = {object3}
        object1.set_dependencies(obj1_dep)
        object2.set_dependencies(obj2_dep)
        self.assertEqual(object1.dependencies, obj1_dep)
        self.assertEqual(object2.dependencies, obj2_dep)

