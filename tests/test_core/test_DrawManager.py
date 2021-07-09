from unittest import TestCase
from geompy.core.DrawManager import DrawManagerMatPlotLib
from geompy.core.PrebuiltConstructions import BaseConstruction, EquilateralUnitTriangle


class DrawManagerTestCase(TestCase):
    pass


class DrawManagerMatPlotLibTestCase(DrawManagerTestCase):
    """
    Currently, all this does is make sure objects are created as expected and no exceptions are thrown.
    TODO: Modify unittests to assert correctness of plt objects.
    """
    def setUp(self):
        self.draw_manager = DrawManagerMatPlotLib()
        self.construction = EquilateralUnitTriangle()

    def test_draw_point(self):
        for point in self.construction.points:
            assert self.draw_manager.draw_point(point)

    def test_draw_line(self):
        for line in self.construction.lines:
            assert self.draw_manager.draw_line(line)

    def test_draw_circle(self):
        for circle in self.construction.circles:
            assert self.draw_manager.draw_circle(circle)

    def test_draw_construction(self):
        assert self.draw_manager.draw_construction(self.construction)

    def test_save_construction(self):
        self.skipTest('Not yet implemented a unittest for saving constructions')

    def test_render(self):
        self.draw_manager.render(self.construction)
        self.draw_manager(self.construction)