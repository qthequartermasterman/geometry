from Point import Point
from Line import Line
from Circle import Circle
import matplotlib.pyplot as plt
import math
import random
from decimal import Decimal

class Construction:
    def __init__(self):
        self.points: {Point} = set()
        self.lines: {Line} = set()
        self.circles: {Circle} = set()
        self.steps = []

    def find_intersections(self, object1, object2) -> {Point}:
        intersections = None
        if type(object1) is Line:
            if type(object2) is Line:
                intersections = self.find_intersections_line_line(object1, object2)
            elif type(object2) is Circle:
                intersections = self.find_intersections_line_circle(object1, object2)
        elif type(object1) is Circle:
            if type(object2) is Line:
                intersections = self.find_intersections_line_circle(object2, object1)
            elif type(object2) is Circle:
                intersections = self.find_intersections_circle_circle(object1, object2)
        if intersections is not None:
            previous_number_of_points = len(self.points)
            i = previous_number_of_points
            for intersect in intersections:
                if not intersect.name:
                    #intersect.name = chr(i + ord('a'))
                    intersect.name = f'"{i}"'
                i += 1
            self.points.update(intersections)
            return intersections
        else:
            print(f'Cannot find intersection of unsupported objects: \n\t{object1}\n\t{object2}')
            raise NotImplementedError

    @staticmethod
    def find_intersections_line_line(line1: Line, line2: Line) -> {Point}:
        """ In the Euclidean plane, two lines can intersect at most once (by Postulate 5/Playfair's Axiom)
            Consequently, this method returns either the empty set (if the lines are parallel/coinciding) or a set
            with one point (if they intersect).

            :param line1
            :param line2

            :returns {Point} a set of at most one point representing the intersection of the two lines
        """
        if line1.slope != line2.slope:
            def line(p1, p2):
                """Adapted from: https://stackoverflow.com/a/20679579"""
                A = (p1.y - p2.y)
                B = (p2.x - p1.x)
                C = (p1.x * p2.y - p2.x * p1.y)
                return A, B, -C

            L1 = line(line1.point1, line1.point2)
            L2 = line(line2.point1, line2.point2)

            D = Decimal(L1[0] * L2[1] - L1[1] * L2[0]).quantize(Decimal(10)**-16)
            Dx = L1[2] * L2[1] - L1[1] * L2[2]
            Dy = L1[0] * L2[2] - L1[2] * L2[0]
            if D != 0:
                x = Dx / D
                y = Dy / D
                return {Point(x, y)}
            else:
                return {}
        else:
            return {}

        '''
        if line1.slope != line2.slope:  # Different slopes guarantees intersection (by Postulate 5)
            x = (line2.intercept - line1.intercept) / (line1.slope - line2.slope)
            y = line1.slope * x + line1.intercept
            return {Point(x, y)}
        else:  # Parallel or coinciding -> no intersection
            return {}
        '''

    @staticmethod
    def find_intersections_line_circle(line, circle) -> {Point}:
        """ In the Euclidean plane, a line can intersect a circle at most twice. Curiously, I am not aware of anywhere
        that Euclid proves this. This is almost trivial to prove when dealing with real coordinates.

            :param line: a line object representing the line in the euclidean space
            :param circle: a circle in the euclidean space

            :returns {Point} a set of at most one point representing the intersection of the two lines
        """
        # We can represent our line as all vectors p so that p = p1+t(p2-p1) where p1, p2 are our original points
        line_basis_vector = line.point2 - line.point1
        # Circle is all points p so that |p-c|=r where c is the center
        # substituting the original line equation in for the circle equation, we get a quadratic equation
        # at^2+bt+c=0 where:
        a = line_basis_vector * line_basis_vector  # Dot product
        b = line_basis_vector * (line.point1 - circle.center) * 2
        c = line.point1 * line.point1 + circle.center * circle.center - (
                    line.point1 * circle.center) * 2 - circle.radius ** 2

        discriminant = b ** 2 - 4 * a * c
        if discriminant < 0:  # There are no real solutions, so the line and circle do not intersect on the plane
            return {}
        elif discriminant == 0:  # The line is tangent and there is one real solution
            t_solution = -b / (2 * a)
            point_solution = line.point1 + line_basis_vector * t_solution
            return {point_solution}
        else:  # The discriminant is positive, so there are two real solutions and the line is secant
            t_solution1 = (-b + Decimal.sqrt(discriminant)) / (2 * a)
            t_solution2 = (-b - Decimal.sqrt(discriminant)) / (2 * a)
            p_solution1 = line.point1 + line_basis_vector * t_solution1
            p_solution2 = line.point1 + line_basis_vector * t_solution2
            return {p_solution1, p_solution2}

    @staticmethod
    def find_intersections_circle_circle(circle1: Circle, circle2: Circle) -> {Point}:
        center1 = circle1.center
        r1 = circle1.radius
        center2 = circle2.center
        r2 = circle2.radius
        diff_between_centers = center2 - center1
        distance_between_centers = abs(diff_between_centers)
        if distance_between_centers > r1 + r2:  # Circles are too far apart to intersect
            return {}
        elif distance_between_centers < abs(r1 - r2):  # One circle contained in other
            return {}
        elif distance_between_centers == 0:  # Circles have same center and are either coincident or the other is contained within the one
            return {}
        else:
            dis_to_area_center = (r1 ** 2 - r2 ** 2 + distance_between_centers ** 2) / (2 * distance_between_centers)
            center_of_intersection_area = center1 + dis_to_area_center * diff_between_centers * (
                    1 / distance_between_centers)
            if dis_to_area_center == r1:  # The two circles are tangent and thus intersect at exactly one point
                return {center_of_intersection_area}
            else:  # Two circles intersect at two points
                height = (r1 ** 2 - dis_to_area_center ** 2).quantize(Decimal('1.0')**16).sqrt()
                x2 = center_of_intersection_area.x
                y2 = center_of_intersection_area.y
                x3 = x2 + height * (center2.y - center1.y) * (1 / distance_between_centers)
                y3 = y2 - height * (center2.x - center1.x) * (1 / distance_between_centers)
                x4 = x2 - height * (center2.y - center1.y) * (1 / distance_between_centers)
                y4 = y2 + height * (center2.x - center1.x) * (1 / distance_between_centers)
                return {Point(x3, y3), Point(x4, y4)}

    def make_matplotlib_diagram(self):
        plt.axes()
        ax = plt.gca()
        for circ in self.circles:
            ax.add_artist(circ.plt_draw())
        for line in self.lines:
            plt_line = line.plt_draw()
            # plt_line.set_transform(ax.transAxes)
            ax.add_line(plt_line)
        x = []
        y = []
        for point in self.points:
            x.append(point.x)
            y.append(point.y)

            ax.add_artist(point.plt_draw())
            plt.annotate(point.name, xy=(point.x, point.y))
        plt.plot(x, y, 'o', color='black')
        plt.axis('equal')
        # plt.axis('image')
        return plt

    def draw_construction(self, filename=None):
        plt = self.make_matplotlib_diagram()
        plt.show()
        if filename:
            self.save_construction(filename)
        plt.close()

    def save_construction(self, filename_stem, notes=''):
        plt = self.make_matplotlib_diagram()
        plt.savefig(filename_stem+'.png')
        with open(f'{filename_stem}.txt', 'a+') as f:
            f.write(str(self) + f'\n{notes}\n\n')
        plt.close()


    def update_intersections_with_object(self, object):
        """TODO: Find a way to do this in less than O(n) time, where n is the number of shapes"""
        intersections: {Point} = set()
        for line in self.lines-{object}:
            intersections.update(self.find_intersections(object, line))
        for circle in self.circles-{object}:
            intersections.update(self.find_intersections(object, circle))
        self.points.update(intersections)
        return intersections

    def check_lengths(self, length: Decimal):
        """

        :param length:
        :return:
        """
        for point1 in self.points:
            for point2 in self.points-{point1}:
                if abs(point2-point1) == length:
                    print(f'Length {length} found between points: {point1} and {point2}')
                    return f'Length {length} found between points: {point1} and {point2}'
        return False

    def get_present_lengths(self):
        lengths_dict = {}
        for point1 in self.points:
            for point2 in self.points-{point1}:
                lengths_dict[abs(point2-point1)] = (point1, point2)
        return lengths_dict

    def add_circle(self, center: Point, point2: Point, counts_as_step=True) -> Circle:
        circle = Circle(center=center, point2=point2)
        self.circles.add(circle)
        if counts_as_step:
            self.steps.append(circle)
        self.update_intersections_with_object(circle)
        return circle

    def add_line(self, point1: Point, point2: Point, counts_as_step=True) -> Line:
        line = Line(point1=point1, point2=point2)
        self.lines.add(line)
        if counts_as_step:
            self.steps.append(line)
        self.update_intersections_with_object(line)
        return line

    def add_random_construction(self, number_of_times=1):
        """

        :param number_of_times:
        :return: the last construction added to the diagram
        """
        construction = None
        for _ in range(number_of_times):
            action = random.choice([self.add_circle, self.add_line])
            point1 = random.choice(tuple(self.points))
            point2 = random.choice(tuple(self.points-{point1}))
            construction = action(point1, point2)
        return construction

    def __len__(self):
        return len(self.steps)

    def __hash__(self):
        return hash((tuple(self.points), tuple(self.steps)))

    def __repr__(self):
        return repr(self.points) + repr(self.steps)

    def __str__(self):
        return f'Construction of length {len(self)} and {len(self.points)} points:\n' + '\n'.join(map(repr, self.points)) + \
               '\n\n' + '\n'.join(map(repr, self.steps))
