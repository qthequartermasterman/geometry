from matplotlib import pyplot as plt
from geompy import Point, Line, Circle, Construction


class DrawManager:
    """Abstract base class whose subclasses contain functionality to draw a construction in a given environment."""

    def draw_point(self, point: Point):
        pass

    def draw_line(self, line: Line):
        pass

    def draw_circle(self, circle: Circle):
        pass

    def draw_construction(self, construction: Construction):
        pass

    def save_construction(self, filename_stem: str, construction_drawing: plt, notes: str = ''):
        pass

    def render(self, construction: Construction, filename: str = ''):
        pass

    def __call__(self, *args, **kwargs):
        return self.render(*args, **kwargs)


class DrawManagerMatPlotLib(DrawManager):
    def __init__(self):
        self.plt = plt

    def draw_point(self, point: Point) -> plt.Circle:
        return self.plt.Circle((float(point.x), float(point.y)), radius=0.02)

    def draw_line(self, line: Line) -> plt.Line2D:
        """
        :return: plt.Line2D representing a matplotlib pyplot line representing our Line.
        """
        return self.plt.Line2D((float(line.point1.x), float(line.point2.x)),
                               (float(line.point1.y), float(line.point2.y)))

    def draw_circle(self, circle: Circle) -> plt.Circle:
        """
        :return: plt.Circle representing a matplotlib pyplot circle representing our circle.
        """
        return self.plt.Circle((float(circle.center.x), float(circle.center.y)),
                               radius=circle.radius.evalf(), fill=False)

    def draw_construction(self, construction: Construction):
        """
                Create a matplotlib diagram with the construction
                :return: the pyplot drawing.
                """
        self.plt.axes()
        ax = self.plt.gca()
        for circle in construction.circles:
            ax.add_artist(self.draw_circle(circle))
        for line in construction.lines:
            plt_line = self.draw_line(line)
            # plt_line.set_transform(ax.transAxes)
            ax.add_line(plt_line)
        x = []
        y = []
        for point in construction.points:
            x.append(point.x)
            y.append(point.y)

            ax.add_artist(self.draw_point(point))
            self.plt.annotate(point.name, xy=(point.x, point.y))
        self.plt.plot(x, y, 'o', color='black')
        self.plt.axis('equal')
        # plt.axis('image')
        return self.plt

    def save_construction(self, filename_stem: str, construction_drawing: plt, notes: str = '') -> None:
        """
        Save a construction to disc. This includes a diagram to filename_stem.png and the steps to filename_step.txt.
        :param construction_drawing:
        :param filename_stem: file path to save to (excluding file type)
        :param notes: Any additional notes to include at the end of the text file.
        :return:
        """
        plot = construction_drawing
        plot.savefig(filename_stem + '.png')
        with open(f'{filename_stem}.txt', 'a+') as f:
            f.write(str(self) + f'\n{notes}\n\n')
        plot.close()

    def render(self, construction: Construction, filename: str = '') -> None:
        """
        Make a matplotlib diagram and display it to the screen and optionally to file.
        If filename is not None, then it will also save the diagram to file.
        :param construction:
        :param filename: the file name to save the diagram to, or None if no file is desired.
        :return: None
        """
        plot = self.draw_construction(construction)
        plot.show()
        if filename:
            self.save_construction(filename_stem=filename, construction_drawing=construction)
        plot.close()

