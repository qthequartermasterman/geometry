import random
from decimal import Decimal
from typing import Union

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from skimage import draw

from Circle import Circle
from Line import Line
from Point import Point


class Construction:
    def __init__(self, name=''):
        self.points: {Point} = set()
        self.lines: {Line} = set()
        self.circles: {Circle} = set()
        self.steps = []
        self.name = name

        # Member variables for our automated construction hunting
        self.interesting_points: {Point} = set()
        self.interesting_lines: {Line} = set()
        self.interesting_circles: {Circle} = set()

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
                intersect.dependencies.update({object1, object2})
                if not intersect.name:
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

            :param line1 is the first Line object
            :param line2 is the second Line object

            :returns {Point} a set of at most one point representing the intersection of the two lines
        """
        if line1.slope != line2.slope:
            def line(p1, p2):
                """Adapted from: https://stackoverflow.com/a/20679579"""
                a = (p1.y - p2.y)
                b = (p2.x - p1.x)
                c = (p1.x * p2.y - p2.x * p1.y)
                return a, b, -c

            l1 = line(line1.point1, line1.point2)
            l2 = line(line2.point1, line2.point2)

            d = Decimal(l1[0] * l2[1] - l1[1] * l2[0]).quantize(Decimal(10) ** -16)
            dx = l1[2] * l2[1] - l1[1] * l2[2]
            dy = l1[0] * l2[2] - l1[2] * l2[0]
            if d != 0:
                x = dx / d
                y = dy / d
                return {Point(x, y)}
            else:
                return {}
        else:
            return {}

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
        elif distance_between_centers == 0:
            # Circles that have same center are either coincident or one is contained within the other
            return {}
        else:
            dis_to_area_center = (r1 ** 2 - r2 ** 2 + distance_between_centers ** 2) / (2 * distance_between_centers)
            center_of_intersection_area = center1 + dis_to_area_center * diff_between_centers * (
                    1 / distance_between_centers)
            if dis_to_area_center == r1:  # The two circles are tangent and thus intersect at exactly one point
                return {center_of_intersection_area}
            else:  # Two circles intersect at two points
                height = (r1 ** 2 - dis_to_area_center ** 2).quantize(Decimal('1.0') ** 8).sqrt()
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
        plot = self.make_matplotlib_diagram()
        plot.show()
        if filename:
            self.save_construction(filename)
        plot.close()

    def save_construction(self, filename_stem, notes=''):
        plot = self.make_matplotlib_diagram()
        plot.savefig(filename_stem + '.png')
        with open(f'{filename_stem}.txt', 'a+') as f:
            f.write(str(self) + f'\n{notes}\n\n')
        plot.close()

    def update_intersections_with_object(self, object):
        """TODO: Find a way to do this in less than O(n) time, where n is the number of shapes"""
        intersections: {Point} = set()
        for line in self.lines - {object}:
            intersections.update(self.find_intersections(object, line))
        for circle in self.circles - {object}:
            intersections.update(self.find_intersections(object, circle))
        self.points.update(intersections)
        return intersections

    def check_lengths(self, length: Decimal):
        """

        :param length:
        :return:
        """
        for point1 in self.points:
            for point2 in self.points - {point1}:
                if abs(point2 - point1) == length:
                    print(f'Length {length} found between points: {point1} and {point2}')
                    return f'Length {length} found between points: {point1} and {point2}'
        return False

    def get_present_lengths(self):
        lengths_dict = {}
        for point1 in self.points:
            for point2 in self.points - {point1}:
                lengths_dict[abs(point2 - point1)] = (point1, point2)
        return lengths_dict

    def add_circle(self, center: Point, point2: Point, counts_as_step=True, interesting=False) -> Circle:
        circle = Circle(center=center, point2=point2)
        self.circles.add(circle)
        if counts_as_step:
            self.steps.append(circle)
        if interesting:
            self.interesting_circles.add(circle)
        self.update_intersections_with_object(circle)
        return circle

    def add_line(self, point1: Point, point2: Point, counts_as_step=True, interesting=False) -> Line:
        line = Line(point1=point1, point2=point2)
        self.lines.add(line)
        if counts_as_step:
            self.steps.append(line)
        if interesting:
            self.interesting_lines.add(line)
        self.update_intersections_with_object(line)
        return line

    def add_point(self, point: Point, interesting=False):
        self.points.add(point)
        if interesting:
            self.interesting_points.add(point)
        return point

    def add_random_construction(self, number_of_times=1):
        """

        :param number_of_times:
        :return: the last construction added to the diagram
        """
        construction = None
        for _ in range(number_of_times):
            prebuilt_steps = self.steps[:]
            construction_is_new = False
            while not construction_is_new:
                action = random.choice([self.add_circle, self.add_line])
                point1 = random.choice(tuple(self.points))
                point2 = random.choice(tuple(self.points - {point1}))
                construction = action(point1, point2)
                construction_is_new = construction not in prebuilt_steps

        return construction

    @staticmethod
    def _point_to_image_space(point: Union[Point, np.array], boundary_radius: int, resolution: int) -> np.array:
        origin = np.array([resolution / 2, resolution / 2])
        if type(point) is Point:
            point = point.numpy()
        return (point * resolution / (2 * boundary_radius) + origin).round().astype(np.uint16)

    @staticmethod
    def _image_to_point_space(pixel_coordinates: np.array, boundary_radius: int, resolution: int) -> np.array:
        pix_origin = np.array([resolution/2, resolution/2])
        return (pixel_coordinates - pix_origin) * (2 * boundary_radius) / resolution

    def get_nearest_point(self, pixel_coordinates: np.array, boundary_radius: int, resolution: int) -> Point:
        point_space = self._image_to_point_space(pixel_coordinates, boundary_radius, resolution)
        closest_point: Point = None
        closest_distance: float = float('inf')
        for point in self.points:
            distance = np.linalg.norm(point.numpy() - point_space)
            if distance < closest_distance:
                closest_point = point
                closest_distance = distance

        return closest_point

    def _interpret_action(self, action, boundary_radius, resolution: int) -> (bool, Point, Point):
        """

        :param action: A number or gym discrete action
        :param resolution: int representing how many pixels are in the image space lengthwise
        :return:
        """
        action = int(action)  # In case the action is stored as something other than an int
        # We define the last bit to be whether or not the action is drawing a line.
        # True = line, False = circle
        is_line = bool(action % 2)
        action = action >> 1

        # Now, we get the next few coordinates by using divmod with a dividend of resolution
        action, point1x = divmod(action, resolution)
        action, point1y = divmod(action, resolution)
        action, point2x = divmod(action, resolution)
        action, point2y = divmod(action, resolution)

        point1 = self.get_nearest_point(np.array([point1x, point1y]), boundary_radius, resolution)
        point2 = self.get_nearest_point(np.array([point2x, point2y]), boundary_radius, resolution)

        return is_line, point1, point2

    def perform_action(self, action, boundary_radius: int, resolution: int):
        """
        Interpret the integer id of the action and perform it in the construction
        :param action: A number or gym discrete action
        :param boundary_radius: 
        :param resolution: int representing how many pixels are in the image space lengthwise
        :return:
        """

        is_line, point1, point2 = self._interpret_action(action, boundary_radius, resolution)
        if is_line:
            self.add_line(point1, point2)
        else:
            self.add_circle(point1, point2)




    @staticmethod
    def _boundary_endpoints_image_space_from_line(line: Line, boundary_radius: int, resolution: int) -> (
    np.array, np.array):
        point1 = line.point1.numpy()
        point2 = line.point2.numpy()
        # Without loss of generality, assume point1 has the smaller y coordinate
        if point1[1] > point2[1]:
            point1, point2 = point2, point1
        # Get the direction vector between the two points
        direction_vector = point2 - point1
        # If the slope > 1 (i.e. the y grows faster than x), we check intersections on the tops. Otherwise the sides
        if abs(direction_vector[0]) < abs(direction_vector[1]):
            dist_to_top = boundary_radius - point1[1]  # Difference from top boundary to the y of p1
            # Scale the direction vector by the distance to top / y of direction_vector
            top_point = point1 + direction_vector * dist_to_top / direction_vector[1]
            # top_point = point1+direction_vector*resolution/(2*boundary_radius)
            # Repeat for bottom
            dist_to_bottom = boundary_radius + point1[1]
            bottom_point = point1 - direction_vector * dist_to_bottom / direction_vector[1]

            # Return the tuple of points
            return Construction._point_to_image_space(top_point, boundary_radius, resolution), \
                   Construction._point_to_image_space(bottom_point, boundary_radius, resolution)
        else:  # Find where it intersects with the sides
            dist_to_right = boundary_radius - point1[0]  # Difference from top boundary to the y of p1
            # Scale the direction vector by the distance to top / y of direction_vector
            right_point = point1 + direction_vector * dist_to_right / direction_vector[0]
            # Repeat for bottom
            dist_to_left = boundary_radius + point1[0]
            left_point = point1 - direction_vector * dist_to_left / direction_vector[0]

            # Return the tuple of points
            return Construction._point_to_image_space(left_point, boundary_radius, resolution), \
                   Construction._point_to_image_space(right_point, boundary_radius, resolution)

    def numpy(self, boundary_radius: int, resolution: int, interesting=False) -> np.array:
        """
        Generate a numpy array that encodes the diagram of this construction.
        :param boundary_radius: int representing how far from the origin we should generate in both x and y directions
        :param resolution: int representing how many pixels we can use in both the x and y directions
        :param interesting: bool specifying if we only include interesting features in the numpy representation
        :return:
        """

        # Indicate interesting if specified, otherwise we will look at all the features
        if interesting:
            point_set = self.interesting_points
            line_set = self.interesting_lines
            circle_set = self.interesting_circles
        else:
            point_set = self.points
            line_set = self.lines
            circle_set = self.circles

        # 1st layer is a grid representing the space. Pixels containing an intersection point has value 1, otherwise 0
        points_array = self._numpy_points(boundary_radius, resolution, point_set)
        # 2nd layer is a grid representing the space. Each pixel has a value equal to number of lines passing through
        lines_array = self._numpy_lines(boundary_radius, resolution, line_set)
        # 3rd layer is a grid representing the space. Each pixel has a value equal to number of circles passing through
        circles_array = self._numpy_circles(boundary_radius, resolution, circle_set)

        # Return the layers stacked together
        return np.stack([points_array, lines_array, circles_array])

    def _numpy_points(self, boundary_radius: int, resolution: int, point_set: {Point}) -> np.array:
        points_array = np.zeros((resolution, resolution), dtype=np.uint16)  # Encodes all the intersection points

        # 1st layer is a grid representing the space. Pixels containing an intersection point has value 1, otherwise 0
        for point in point_set:
            point_np = self._point_to_image_space(point, boundary_radius, resolution)
            # Check each coordinate. If it's off the screen (i.e. the coordinate is bigger than the resolution), omit
            if point_np[0] >= resolution or point_np[1] >= resolution:
                break
            # Mark the point on the array
            points_array[point_np[0]][point_np[1]] = 1
        return points_array

    def _numpy_lines(self, boundary_radius: int, resolution: int, line_set: {Line}) -> np.array:
        lines_array = np.zeros((resolution, resolution), dtype=np.uint16)  # Encodes all the line pixels
        # 2nd layer is a grid representing the space. Each pixel has a value equal to number of lines passing through
        for line in line_set:
            # point1 = self._point_to_image_space(line.point1, boundary_radius, resolution)
            # point2 = self._point_to_image_space(line.point2, boundary_radius, resolution)
            point1, point2 = self._boundary_endpoints_image_space_from_line(line, boundary_radius, resolution)
            rr, cc = draw.line_nd(point1, point2)
            # Make sure to sort out any points outside of the resolution from rr and cc, so we don't get indexing errors
            # This can happen, since round may round up points on the edge to the pixel just outside the range
            rr, cc = rr[rr < resolution], cc[rr < resolution]
            rr, cc = rr[cc < resolution], cc[cc < resolution]
            rr, cc = rr[rr >= 0], cc[rr >= 0]
            rr, cc = rr[cc >= 0], cc[cc >= 0]
            # Add one to the array, so we know that we can see all the lines at those points.
            lines_array[rr, cc] += 1
        return lines_array

    def _numpy_circles(self, boundary_radius: int, resolution: int, circle_set: {Circle}) -> np.array:
        circles_array = np.zeros((resolution, resolution), dtype=np.uint16)  # Encode all circles' pixels
        for circle in circle_set:
            center = self._point_to_image_space(circle.center, boundary_radius, resolution)
            radius = round(
                circle.radius * resolution / (2 * boundary_radius))  # Convert radius to pixel space by scaling
            rr, cc = draw.circle_perimeter(center[0], center[1], radius, shape=circles_array.shape)
            circles_array[rr, cc] += 1
        return circles_array

    def __len__(self):
        return len(self.steps)

    def __hash__(self):
        return hash((tuple(self.points), tuple(self.steps)))

    def __repr__(self):
        return repr(self.points) + repr(self.steps)

    def __str__(self):
        return f'Construction of length {len(self)} and {len(self.points)} points:\n' + \
               '\n'.join(map(repr, self.points)) + '\n\n' + '\n'.join(map(repr, self.steps))

    def get_dependency_graph(self, zero_index=False):
        """

        :param zero_index: Specifies whether or not the graph elements have labels that start at zero or one.
        :return: object_labels is a dictionary {Object: int} where the keys are objects in the construction and the
        values are assigned indices. Note: If zero_index is not specified, these indices start at 1, not 0, since that
        is the tradition in group theory.
        :return: nx.DiGraph represented directed acyclic graph generated by the lines and circles in a construction. There
        is a directed edge from an object to all other objects that directly depend on it in their construction.
        """
        directed_graph = nx.DiGraph()
        construction_objects = self.steps
        if zero_index:
            labels = range(len(construction_objects))
        else:
            labels = range(1, len(construction_objects) + 1)
        object_labels = dict(map(lambda x, y: (x, y), construction_objects, labels))

        directed_graph.add_nodes_from(object_labels.values())
        for shape in construction_objects:
            for dependency in shape.dependencies:
                directed_graph.add_edge(object_labels[dependency], object_labels[shape])

        return object_labels, directed_graph

    def get_conjugate_constructions(self, zero_index=False):
        """
        I define conjugate constructions as an equivalent construction that generates the exact same diagram.
        This is often possible since not every step in a construction depends on every step before it. In that case, we
        can permute those independent steps. A careful analysis shows, however, that this is equivalent to getting all
        the topological sorts of the directed acyclic graph generated by the lines and circles in a construction. There
        is a directed edge from an object to all other objects that directly depend on it in their construction.

        :return: object_labels is a dictionary {Object: int} where the keys are objects in the construction and the
        values are assigned indices. Note: If zero_index is not specified, these indices start at 1, not 0, since that
        is the tradition in group theory.
        :return: sorts_list is a list of lists that each represent a different topological sort of indices
        """
        object_labels, directed_graph = self.get_dependency_graph(zero_index)

        sorts = nx.algorithms.dag.all_topological_sorts(directed_graph)
        sorts_list = list(sorts)
        return object_labels, sorts_list

    def plain_text(self, boundary_radius: int, resolution: int, interesting=False):
        numpy = self.numpy(boundary_radius, resolution, interesting)
        numpy = numpy.sum(axis=0)  # Condense everything to one matrix.
        for row in numpy:
            line_string = ''  # Store each line
            for column in row:
                line_string += '*' if column > 0 else ' '
            print(line_string)
