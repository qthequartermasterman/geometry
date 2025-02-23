import itertools
import random
from enum import Enum
from typing import Union

import networkx as nx
import numpy as np
from skimage import draw

from geompy.cas import Expr, sqrt, Infinity
from geompy.cas import alphabet
from geompy.core import Circle, Line, Point
from .Angle import Angle
from .Object import Object


class ConstructionMode(Enum):
    """
    Enum containing the different modes for a self.
    This allows you to limit the tools (compass/circles or lines/straightedge) you can use to build constructions.
    DEFAULT: Both compass and straightedge are considered valid tools.
    LINES_ONLY: Only straightedges are considered valid tools. Compasses are forbidden
    CIRCLES_ONLY: Only compasses are considered valid tools. Straightedges are forbidden
    """
    DEFAULT = 0
    LINES_ONLY = 1
    CIRCLES_ONLY = 2


class Construction:
    """
    Constructions contain all of the processes necessary to perform a traditional Euclidean Compass-and-Straightedge
    Construction.

    Constructions are sets of points, lines, and circles, such that lines and circles are defined solely from the
    aforementioned set of points. Additionally, lines, circles, and points must be "iteratively generated" from an
    initial set of points.

    In a Euclidean self, the only valid actions are:
    1. Pick 2 points from the set of constructed points, and draw a line through them.
    2. Pick 2 points from the set of constructed points, and draw a circle with the first as the center and the second
    as a radius, or
    3. Pick 2 points from the set of constructed points, and draw a circle with the first as the radius and the second
    as the center.

    After any of those actions, the intersections of that new object and any pre-existing objects are then added to the
    set of points.

    Euclid's elements show that these three actions are sufficient to "construct" a significant number of points and
    shapes. For example, Euclid's Book I self 1 creates an equilateral triangle from 2 points using 3 lines and
    2 circles.

    For convenience sake, the Construction class also maintains a list and set of steps. The list is ordered, so that
    we can know exactly what order to draw the steps to recreate the self. The set is (obviously) unordered,
    so that two constructions with the same sets but in different orders (which thus create the same points) can be
    considered equivalent.

    Additionally, for convenience, we also maintain a set of "interesting" points, lines, and circles, since a given
    self can have _many_ intermediate steps, that although necessary for the self, do little else other
    than clutter and confuse.

    Finally, also for convenience, we maintain a set of "actions" representing the valid actions at any given time, so
    we do not have to compute them each step.
    """

    def __init__(self, name='', construction_mode=ConstructionMode.DEFAULT):
        # Fundamental sets--points, lines and circles
        self.points: {Point} = set()
        self.lines: {Line} = set()
        self.circles: {Circle} = set()

        # Optional Name
        self.name = name

        # Steps list and set, as explained above.
        self.steps: [Line, Circle] = []
        self.steps_set: {Line, Circle} = set()

        # Member variables for our automated self hunting
        self.interesting_points: {Point} = set()
        self.interesting_lines: {Line} = set()
        self.interesting_circles: {Circle} = set()

        # Set containing all the possible actions at any given moment in time.
        self._actions: {Union[Line, Circle]} = set()
        self.new_points_since_last_actions_update: {Point} = set()

        # Enum specifying what type of mode this self should be.
        self.construction_mode = construction_mode

    # @lru_cache()
    def find_intersections(self, object1, object2, interesting=True) -> {Point}:
        intersections = None
        if isinstance(object1, Line):
            if isinstance(object2, Line):
                intersections = self.find_intersections_line_line(object1, object2)
            elif isinstance(object2, Circle):
                intersections = self.find_intersections_line_circle(object1, object2)
        elif isinstance(object1, Circle):
            if isinstance(object2, Line):
                intersections = self.find_intersections_line_circle(object2, object1)
            elif isinstance(object2, Circle):
                intersections = self.find_intersections_circle_circle(object1, object2)
        if intersections is not None:
            previous_number_of_points = len(self.points)
            i = previous_number_of_points
            for intersect in intersections:
                intersect.dependencies.update({object1, object2})
                if not intersect.name:
                    # intersect.name = f'"{i}"'
                    intersect.name = alphabet(i)
                i += 1
            self.points.update(intersections)
            if interesting:
                self.interesting_points.update(intersections)
            return intersections
        else:
            raise NotImplementedError(f'Cannot find intersection of unsupported objects: \n\t{object1}\n\t{object2}')

    # @lru_cache()
    @staticmethod
    def find_intersections_line_line(line1: Line, line2: Line) -> {Point}:
        """
        In the Euclidean plane, two lines can intersect at most once (by Postulate 5/Playfair's Axiom).
        Consequently, this method returns either the empty set (if the lines are parallel/coinciding) or a set
        with one point (if they intersect).

        :param line1 is the first Line object
        :param line2 is the second Line object

        :returns {Point} a set of at most one point representing the intersection of the two lines
        """
        if line1.slope != line2.slope:
            if line1.slope is Infinity:
                # Line 1 is vertical, use its x value as the x value to evaluate line2
                x = line1.point1.x
                y = line2(x)
            elif line2.slope is Infinity:
                # Line 2 is vertical, use its x value as the x value to evaluate line1
                x = line2.point1.x
                y = line1(x)
            else:
                x = (line2.intercept - line1.intercept) / (line1.slope - line2.slope)
                y = line1(x)
            return {Point(x, y)}
        else:
            return {}

    # @lru_cache()
    @staticmethod
    def find_intersections_line_circle(line, circle) -> {Point}:
        """
        In the Euclidean plane, a line can intersect a circle at most twice. Curiously, I am not aware of anywhere
        that Euclid proves this. This is almost trivial to prove when dealing with real coordinates.

        :param line: a line object representing the line in the euclidean space
        :param circle: a circle in the euclidean space
        :returns {Point} a set of at most one point representing the intersection of the two lines
        """
        # In summary, the algorithm below takes the equation of the line, substitutes it in
        # for y in the circle equation, then solves for x. It then takes that x value, and
        # substitutes it into the equation of the line to get the y.

        m = line.slope
        b = line.intercept
        x0 = circle.center.x
        y0 = circle.center.y
        r = circle.radius
        if m is Infinity or b is Infinity:
            # When dealing with vertical lines, we need to be a bit more clever.
            # Use the equation of a circle in the plane, and solve for y, using the x-coordinate of the line as x
            x = line.point1.x
            inside_sqrt = r ** 2 - (x - x0) ** 2
            return {Point(x, y0 + sqrt(inside_sqrt)), Point(x, y0 - sqrt(inside_sqrt))}

        diff = b - y0  # This subtraction shows up frequently. This is just so we do not need to repeat it.

        # Coefficients of the substituted equation in terms of x. When expanded, it forms a quadratic equation on x.
        coefficient_a = 1 + m ** 2
        # Technically, the B coefficient is twice this quantity, but we will be factoring out a 2 of everything else
        # later on.
        coefficient_b = -x0 + m * diff
        # Technically, the C coefficient is twice this quantity, but we will be factoring out a 2 of everything else
        # later on.
        coefficient_c = x0 ** 2 + diff ** 2 - r ** 2

        # Again, the discriminant should be $b^2-4ac$, but we can simplify the quadratic equation in this case by
        # factoring out the aforementioned 2
        discriminant = coefficient_b ** 2 - coefficient_a * coefficient_c
        if discriminant < 0:  # There are no real solutions, so the line and circle do not intersect on the plane
            return {}
        elif discriminant == 0:  # The line is tangent and there is one real solution
            x = -coefficient_b / coefficient_a
            y = line(x)
            return {Point(x, y)}
        else:  # The discriminant is positive, so there are two real solutions and the line is secant
            x1 = (-coefficient_b + sqrt(discriminant)) / coefficient_a
            x2 = (-coefficient_b - sqrt(discriminant)) / coefficient_a
            y1 = line(x1)
            y2 = line(x2)
            return {Point(x1, y1), Point(x2, y2)}

    # @lru_cache()
    @staticmethod
    def find_intersections_circle_circle(circle1: Circle, circle2: Circle) -> {Point}:
        """
        Find the intersection points between two circles.
        :param circle1: first circle
        :param circle2: second circle
        :return: Set of points showing all the intersection points between the two circles.
        """
        # Determine some constants, for easy access
        center1 = circle1.center
        r1 = circle1.radius
        center2 = circle2.center
        r2 = circle2.radius
        diff_between_centers = center2 - center1
        distance_between_centers = abs(diff_between_centers)
        if hasattr(distance_between_centers, 'evalf'):
            dis_evalf = distance_between_centers.evalf()
            # print(distance_between_centers, dis_evalf)
            if not hasattr(dis_evalf, '__float__'):
                raise ValueError(f'dis_evalf has no float attribute: {type(dis_evalf)} {dis_evalf}')
            distance_between_centers_float = float(dis_evalf)
        else:
            print(f'{distance_between_centers} has no evalf property.')
            distance_between_centers_float = float(distance_between_centers)

        # Determine if the circles even do intersect. There are four cases:
        # 1. Centers are the same => Cannot intersect (either coincident or one contained in other)
        # 2. Circles are further apart than the sum of their radius => Cannot intersect (too far apart)
        # 3. Circles are close than the absolute value of the difference of radius => Cannot intersect(one inside other)
        # 4. Otherwise => Circles intersect
        # Note that in the 4th case, we can find two sub-cases, where the circles are tangent (and thus intersect once)
        # or where the circles intersect twice. Technically, we could just handle the second sub-case, but we separate
        # them here for computational speed.
        if distance_between_centers == 0:
            # Circles that have same center are either coincident or one is contained within the other
            return set()
        elif distance_between_centers_float > float((r1 + r2).evalf()):
            # Circles are too far apart to intersect
            return set()
        elif distance_between_centers_float < float(abs(r1 - r2).evalf()):
            # One circle contained in other
            return set()
        else:
            # For certain, our circles intercept.
            # Calculate the distance to the intersection area center.
            distance_recip = (1 / distance_between_centers)
            dis_to_area_center = (r1 ** 2 - r2 ** 2 + distance_between_centers ** 2) / (2 * distance_between_centers)
            # Calculate the center of the intersection area
            center_of_intersection_area = center1 + dis_to_area_center * diff_between_centers * distance_recip
            if dis_to_area_center == r1:
                # The two circles are tangent and thus intersect at exactly one point
                # Technically this check is unnecessary, since the below computation will return two equal points.
                # But to save on speed, we can just return the center point, since we know that is the single
                # intersection point
                return {center_of_intersection_area}
            else:
                # Two circles intersect at two points
                height = sqrt(r1 ** 2 - dis_to_area_center ** 2)
                x2 = center_of_intersection_area.x
                y2 = center_of_intersection_area.y
                diff_y = center2.y - center1.y
                diff_x = center2.x - center1.x
                height_times_distance_recip = height * distance_recip
                y_displacement = diff_y * height_times_distance_recip
                x_displacement = diff_x * height_times_distance_recip

                x3 = x2 + y_displacement
                y3 = y2 - x_displacement
                x4 = x2 - y_displacement
                y4 = y2 + x_displacement
                return {Point(x3, y3), Point(x4, y4)}

    def find_point(self, point: Point):
        """
        Find a given point in the given self. Although two points are considered equal if they have the same
        coordinates, their names and dependencies may differ. This information can sometimes be useful. So we can return
        the equivalent point within a self.
        :param point: a point to find in the self.
        :return: the point within the set equal to the given one.
        """
        for internal_point in self.points:
            if internal_point == point:
                return internal_point
        return None

    def update_intersections_with_object(self, obj: Object) -> {Point}:
        """
        Calculate the set of intersection points with the given object and all other objects in the self.

        TODO: Find a way to do this in less than O(n) time, where n is the number of shapes

        :param obj: the other object of which we should calculate the intersections with.
        :return: a set of intersection points
        """
        # The set of intersection points we will eventually return.
        intersections: {Point} = set()
        # Check every line except our given object
        for line in self.lines - {obj}:
            intersections.update(self.find_intersections(obj, line))
        # check every circle except our given object
        for circle in self.circles - {obj}:
            intersections.update(self.find_intersections(obj, circle))

        # Update the set of points to include the newly-found intersection points
        self.points.update(intersections)

        # Return our result
        return intersections

    def check_lengths(self, length: Expr) -> bool:
        """
        Check every length in a self and compare against the given length

        :param length: the desired length to find in a self.
        :return: string containing the two points and length
        """
        for point1 in self.points:
            for point2 in self.points - {point1}:
                if abs(point2 - point1) == length:
                    print(f'Length {length} found between points: {point1} and {point2}')
                    return True
        return False

    def get_present_lengths(self) -> {Expr: (Point, Point)}:
        """
        Get a dictionary with keys all of the present length and values the pair of points that make that length.
        :return: dictionary with keys all of the present length and values the pair of points that make that length.
        """
        lengths_dict = {}
        for point1 in self.points:
            for point2 in self.points - {point1}:
                lengths_dict[abs(point2 - point1)] = (point1, point2)
        return lengths_dict

    def add_circle(self, center: Point, point2: Point,
                   counts_as_step: bool = True, interesting: bool = False) -> Circle:
        """
        Add a circle to the self with a given center and radius point.
        :param center: center point of the the circle
        :param point2: radius point of the circle
        :param counts_as_step: if true, the step will be added to the steps list/set. If false, not.
        :param interesting:  if true, the step will be added to interesting circles.
        :return: the generated circle
        """
        circle = Circle(center=center, point2=point2)
        self.add_step_premade(circle, counts_as_step=counts_as_step, interesting=interesting)
        return circle

    def add_line(self, point1: Point, point2: Point, counts_as_step=True, interesting=False) -> Line:
        """
        Add a line to the self with the given generating points.
        :param point1: first generating point of line
        :param point2: second generating point of line
        :param counts_as_step: if true, the step will be added to the steps list/set. If false, not.
        :param interesting: if true, the step will be added to interesting circles.
        :return: the generated line
        """
        line = Line(point1=point1, point2=point2)
        self.add_step_premade(line, counts_as_step=counts_as_step, interesting=interesting)
        return line

    def add_step_premade(self, step: Object, counts_as_step=True, interesting=False) -> Union[Circle, Line]:
        """

        :param step:
        :param counts_as_step:
        :param interesting:
        :return:
        """
        # Check the type of this step, so we can add it to the correct set
        # Then add it to the correct set (and interesting set if interesting)
        if isinstance(step, Line):
            if step in self.lines:
                # If it already exists, then we can skip adding it.
                return step
            self.lines.add(step)
            if interesting:
                self.interesting_lines.add(step)
        elif isinstance(step, Circle):
            if step in self.circles:
                # If it already exists, then we can skip adding it.
                return step
            self.circles.add(step)
            if interesting:
                self.interesting_circles.add(step)
        else:
            raise TypeError(f'Cannot add step {step} of type {type(step)} to a construction.')
        # If the step should count as a step, add it to those sets.
        if counts_as_step:
            self.steps.append(step)
            self.steps_set.add(step)
        # Get new points and actions
        new_points = self.update_intersections_with_object(step)
        self.discard_action(step)
        # self.actions = self.get_valid_actions(new_points)
        self.add_points_to_actions_update_queue(new_points)
        return step

    def add_point(self, point: Point, interesting=False) -> Point:
        """
        Add a point to a self.
        :param point: the given point
        :param interesting: Should the point be marked as interesting?
        :return: the point we added
        """
        if point not in self.points:
            if not point.name:
                point.name = alphabet(len(self.points))
            self.points.add(point)
            if interesting:
                self.interesting_points.add(point)
        self.add_points_to_actions_update_queue({point})
        return point

    def add_random_construction(self, number_of_steps=1, interesting=True):
        """
        Add a number of random steps to the self.
        :param interesting: bool representing whether new intersection points should be considered "interesting"
        :param number_of_steps: number of random steps to add
        :return: the last self added to the diagram
        """
        construction = None
        for _ in range(number_of_steps):
            prebuilt_steps = self.steps[:]
            construction_is_new = False
            while not construction_is_new:
                action = random.choice([self.add_circle, self.add_line])
                point1 = random.choice(tuple(self.points))
                point2 = random.choice(tuple(self.points - {point1}))
                construction = action(point1, point2, interesting)
                construction_is_new = construction not in prebuilt_steps

        return construction

    @staticmethod
    def _point_to_image_space(point: Union[Point, np.array], boundary_radius: int, resolution: int) -> np.array:
        """
        Convert a point in point space into a coordinates in image space.
        :param point: Point in point space
        :param boundary_radius: how far the image can go out in either x or y coordinate
        :param resolution: how many pixels are there across the image
        :return: np.array containing the image coordinates of the point.
        """
        origin = np.array([resolution / 2, resolution / 2])
        if type(point) is Point:
            point = point.numpy()
        return (point * resolution / (2 * boundary_radius) + origin).round().astype(np.uint16)

    @staticmethod
    def _image_to_point_space(pixel_coordinates: np.array, boundary_radius: int, resolution: int) -> np.array:
        """
        Convert a set of coordinates in image space to coordinates in point space
        :param pixel_coordinates: np.array holding the pixel coordinates
        :param boundary_radius: how far in point space is included in image
        :param resolution: number of pixels across the image
        :return: np.array containing the coordinates in point space.
        """
        pix_origin = np.array([resolution / 2, resolution / 2])
        return np.array((pixel_coordinates - pix_origin) * (2 * boundary_radius) / resolution)

    def get_nearest_point(self, pixel_coordinates: np.array, boundary_radius: int,
                          resolution: int, not_points: [Point] = None) -> Point:
        """
        Get the nearest point to the given coordinates in pixel space.
        :param pixel_coordinates: Coordinates in pixel space
        :param boundary_radius: how far from the origin in image space can we see
        :param resolution: how many pixels across in the image
        :param not_points: Points to not include in the search
        :return: the nearest point to the given coordinates in pixel space.
        """
        point_space = self._image_to_point_space(pixel_coordinates, boundary_radius, resolution)
        closest_point: Point = None
        closest_distance: float = float('inf')
        for point in self.points:
            if not_points is None or point not in not_points:
                distance = np.linalg.norm(point.numpy() - point_space)
                if distance < closest_distance:
                    closest_point = point
                    closest_distance = distance

        return closest_point

    def _interpret_action(self, action, boundary_radius: int, resolution: int) -> (bool, Point, Point):
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
        action, point1y = divmod(action, resolution)
        action, point1x = divmod(action, resolution)
        action, point2y = divmod(action, resolution)
        action, point2x = divmod(action, resolution)
        # print(f'({point1x}, {point1y}), ({point2x}, {point2y})')

        point1 = self.get_nearest_point(np.array([point1x, point1y]), boundary_radius, resolution)
        point2 = self.get_nearest_point(np.array([point2x, point2y]), boundary_radius, resolution, not_points=[point1])

        return is_line, point1, point2

    def _interpret_action_continuous(self, action: np.array, boundary_radius: int) -> (bool, Point, Point):
        """

        :param action: np.array with shape (5,) where the first two floats are the coordinates
            of the first point, and last two are the last point.
        :param boundary_radius: how far away from the origin is "1 unit"
        :return: bool representing whether the move is drawing a line or circle,
        :return: Point representing the first point
        :return: Point representing the second point
        """
        # print('Action shape', action.shape)
        # print('Action', action)
        is_line = True if action[-1] > 0 else False  # If the last coordinate is positive, line, otherwise circle
        point1 = self.get_nearest_point(action[0:2], boundary_radius, 2)
        point2 = self.get_nearest_point(action[2:4], boundary_radius, 2, not_points=[point1])

        return is_line, point1, point2

    def perform_action(self, action, boundary_radius: int, resolution: int):
        """
        Interpret the integer id of the action and perform it in the self
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

    def perform_action_continuous(self, action: np.array, boundary_radius: int) -> None:
        """
        Interpret the action and perform it in the self
        :param action: np.array with shape (5,) where the first two floats are the coordinates
            of the first point, and last two are the last point.
        :param boundary_radius: how far away from the origin is "1 unit"
        :return:
        """

        is_line, point1, point2 = self._interpret_action_continuous(action, boundary_radius)
        if is_line:
            self.add_line(point1, point2)
        else:
            self.add_circle(point1, point2)

    def update_valid_actions(self, force_calculate=False) -> {Union[Line, Circle]}:
        """
        Finds all the valid actions (lines/circles) that can be drawn on a given self.
        If focus_points is defined then this will find all distinct pairs of points where the first point is in
        focus_points, and the second point is in self.points. No pair can have the same point twice. Otherwise, it
        iterates over all pairs of distinct points.

        Once the pairs of points are chosen, it adds all of the appropriate actions to the self.valid_moves set. An
        action is appropriate if and only if it is permitted in the current self mode
        (DEFAULT/CIRCLES_ONLY/LINES_ONLY) and that object does not already exist in the self.

        TODO: Identify a better algorithm that can determine if an action is valid without generating it first.

        :param: force_calculate: bool representing whether or not to look at all pairs of points for new actions
        :return: Returns a list of circles and lines corresponding to valid moves from the current self
        """
        legal_lines: {Line} = set()  # Set of lines showing legal lines
        legal_circles: {Circle} = set()  # Set of circles showing legal circles

        # Determine the combinations of points to focus on.
        # Since self._actions contains all actions generated by previous points, we can save compute by simply
        # checking all of the new points (defined in focus_points) and pairing them with all of the other points in the
        # self.
        # If focus_points is not defined, we should determine with force_calculate whether to try all the point
        # combinations or simply skip any calculations and return the previously generated actions.

        if force_calculate is True:
            combinations = itertools.combinations(self.points, 2)
        else:
            combinations = itertools.product(self.new_points_since_last_actions_update, self.points)

        # Iterate over all of the pairs and generate possible appropriate actions with that pair of points.
        # If an action is appropriate, add it to the corresponding legal actions set.

        # If we are force calculating all points, we will get non-distinct pairs (where the first and second point are
        # swapped). These non-distinct points generate the same actions, so we can save compute by keeping track of our
        # already used points.
        used_points: {Point} = set()
        for point1, point2 in combinations:
            if point1 != point2:
                # Only check if point1 is already used if we are forcing calculation of all pairs.
                # For some reason I cannot explain, doing it all the time worked reliably in Python>=3.8 but would
                # fail reliably in Python<=3.7. I cannot identify why.
                # The speed-up was minuscule, regardless, when using only focused points. So, little is lost.
                if force_calculate and point1 not in used_points:
                    used_points.add(point1)
                # An action is appropriate if and only if it is permitted in the current self mode
                # (DEFAULT/CIRCLES_ONLY/LINES_ONLY) and that object does not already exist in the self.
                if self.construction_mode in (ConstructionMode.DEFAULT, ConstructionMode.LINES_ONLY):
                    line = Line(point1, point2)
                    if line not in self.lines | legal_lines:
                        legal_lines.add(line)
                if self.construction_mode in (ConstructionMode.DEFAULT, ConstructionMode.CIRCLES_ONLY):
                    circle1 = Circle(center=point1, point2=point2)
                    circle2 = Circle(point2, point2=point1)
                    if circle1 not in self.circles | legal_circles:
                        legal_circles.add(circle1)
                    if circle2 not in self.circles | legal_circles:
                        legal_circles.add(circle2)

        # Finally, update the self.actions to include all of our newly generated actions, then return it.
        self._actions.update(legal_lines | legal_circles)
        # Simplify all the actions so we do not get duplicates
        self._actions = {action.simplify() for action in self._actions}
        # Clear out the points queue
        self.new_points_since_last_actions_update = set()
        return self._actions

    def add_points_to_actions_update_queue(self, focus_points: {Point} = None) -> {Point}:
        """
        Add all of the focus_points to self.new_points_since_last_actions_update. Those points will be used to update
        self.actions the next time self.actions is needed. This gives us the advantage of speed when we do not need
        self.actions, but also lets us save duplicate computations down the line.

        :param focus_points:
        :return: the current points in the update actions queue
        """
        self.new_points_since_last_actions_update.update(focus_points)
        return self.new_points_since_last_actions_update

    def discard_action(self, step: Union[Line, Circle]) -> None:
        self._actions.discard(step)

    @property
    def actions(self):
        return self.update_valid_actions()

    @staticmethod
    def _boundary_endpoints_image_space_from_line(line: Line, boundary_radius: int, resolution: int) -> (
            np.array, np.array):
        """
        Generate the end points of a line in image space. By default, a matplotlib line only draws segments. To extend
        the line to the ends, we need to do some more math.
        :param line: the Line we want to draw
        :param boundary_radius: how far from the origin in point space can we see in the image.
        :param resolution: Number of pixels across the image
        :return: tuple of two np.arrays that each contain pixel coordinates of the line at teh edge.
        """
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
            return (Construction._point_to_image_space(top_point, boundary_radius, resolution),
                    Construction._point_to_image_space(bottom_point, boundary_radius, resolution))
        else:  # Find where it intersects with the sides
            dist_to_right = boundary_radius - point1[0]  # Difference from top boundary to the y of p1
            # Scale the direction vector by the distance to top / y of direction_vector
            right_point = point1 + direction_vector * dist_to_right / direction_vector[0]
            # Repeat for bottom
            dist_to_left = boundary_radius + point1[0]
            left_point = point1 - direction_vector * dist_to_left / direction_vector[0]

            # Return the tuple of points
            return (Construction._point_to_image_space(left_point, boundary_radius, resolution),
                    Construction._point_to_image_space(right_point, boundary_radius, resolution))

    def numpy(self, boundary_radius: int, resolution: int, interesting=False) -> np.array:
        """
        Generate a numpy array that encodes the diagram of this self.
        :param boundary_radius: int representing how far from the origin we should generate in both x and y directions
        :param resolution: int representing how many pixels we can use in both the x and y directions
        :param interesting: bool specifying if we only include interesting features in the numpy representation
        :return: np.array encoding the self as multiple images. The layers represent the points, lines, circles
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
        """
        Generate a numpy array that has only the points in image space.
        :param boundary_radius: int representing how far from the origin we should generate in both x and y directions
        :param resolution: int representing how many pixels we can use in both the x and y directions
        :param point_set: the set of points
        :return: numpy array that encodes the points in image space
        """
        points_array = np.zeros((resolution, resolution), dtype=np.int16)  # Encodes all the intersection points

        # 1st layer is a grid representing the space. Pixels containing an intersection point has value 1, otherwise 0
        for point in point_set:
            point_np = self._point_to_image_space(point, boundary_radius, resolution)
            # Check each coordinate. If it's off the screen (i.e. the coordinate is bigger than the resolution), omit
            if point_np[0] >= resolution or point_np[1] >= resolution:
                break
            # Mark the point on the array
            points_array[point_np[0]][point_np[1]] += 1
        return points_array

    def _numpy_lines(self, boundary_radius: int, resolution: int, line_set: {Line}) -> np.array:
        """
        Generate a numpy array that has only the lines in image space.
        :param boundary_radius: int representing how far from the origin we should generate in both x and y directions
        :param resolution: int representing how many pixels we can use in both the x and y directions
        :param line_set: the set of lines to encode in our image
        :return: numpy array that encodes the lines in image space
        """
        lines_array = np.zeros((resolution, resolution), dtype=np.int16)  # Encodes all the line pixels
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
        """
        Generate a numpy array that has only the circles in image space.
        :param boundary_radius: int representing how far from the origin we should generate in both x and y directions
        :param resolution: int representing how many pixels we can use in both the x and y directions
        :param circle_set: the set of circles to encode in our image
        :return: numpy array that encodes the circles in image space
        """
        circles_array = np.zeros((resolution, resolution), dtype=np.int16)  # Encode all circles' pixels
        for circle in circle_set:
            center = self._point_to_image_space(circle.center, boundary_radius, resolution)
            radius = round(
                circle.radius * resolution / (2 * boundary_radius))  # Convert radius to pixel space by scaling
            rr, cc = draw.circle_perimeter(center[0], center[1], radius, shape=circles_array.shape)
            circles_array[rr, cc] += 1
        return circles_array

    def __len__(self) -> int:
        """
        :return: the length of the steps list (the number of steps in the self)
        """
        return len(self.steps)

    def __hash__(self) -> int:
        """
        Constructions are considered equivalent if they have the same points and steps (regardless of order)
        :return: a unique hash that represents the the self.
        """
        # Turn the steps into a set first, so that permuting the steps doesn't change the equality.
        self.simplify()
        return hash(tuple(sorted(self.steps_set)))

    def __eq__(self, other) -> bool:
        """
        Constructions are considered equivalent if they have the same points and steps (regardless of order)
        :return: true if the two constructions have the same points and steps.
        """
        # If the other is a self, and points and steps match (not necessarily in same order), then equal
        return isinstance(other, Construction) and self.steps_set == other.steps_set

    def __repr__(self) -> str:
        """
        :return: encode all the points and steps in a string
        """
        return repr(self.points) + repr(self.steps)

    def __str__(self) -> str:
        """
        :return: encode all the points and steps in a string
        """
        return f'Construction of length {len(self)} and {len(self.points)} points:\n' + \
               '\n'.join(map(repr, self.points)) + '\n\n' + '\n'.join(map(repr, self.steps))

    def get_dependency_graph(self, zero_index=False):
        """
        Get a networkx graph that encodes the dependency information of each object.

        :param zero_index: Specifies whether or not the graph elements have labels that start at zero or one.
        :return: object_labels is a dictionary {Object: int} where the keys are objects in the self and the
        values are assigned indices. Note: If zero_index is not specified, these indices start at 1, not 0,
        since that is the tradition in group theory.
        :return: nx.DiGraph represented directed acyclic graph generated by the lines and circles in a self.
        There is a directed edge from an object to all other objects that directly depend on it in their self.
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
        I define conjugate constructions as an equivalent self that generates the exact same diagram.
        This is often possible since not every step in a self depends on every step before it. In that case, we
        can permute those independent steps. A careful analysis shows, however, that this is equivalent to getting all
        the topological sorts of the directed acyclic graph generated by the lines and circles in a self. There
        is a directed edge from an object to all other objects that directly depend on it in their self.

        :return: object_labels is a dictionary {Object: int} where the keys are objects in the self and the
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

    def simplify(self):
        self.points = {point.simplify() for point in self.points}
        self.lines = {line.simplify() for line in self.lines}
        self.circles = {circle.simplify() for circle in self.circles}
        self.steps = [step.simplify() for step in self.steps]
        self.steps_set = set(self.steps)
        return self

    @staticmethod
    def check_if_points_on_same_side(line: Line, point1: Point, point2: Point):
        if point1 in line or point2 in line:
            raise ValueError(f'At least one point {point1}, {point2} is on {line}')

        if line.slope == Infinity:
            point1_diff = point1.x - line.point1.x
            point2_diff = point2.x - line.point1.x
            # return (point1_diff > 0 and point2_diff > 0) or (point1_diff < 0 and point2_diff < 0)
            # Check if point1_diff and point2_diff have the same sign.
            return point1_diff * point2_diff > 0
        f_point1 = point1.y - line(point1.x)
        f_point2 = point2.y - line(point2.x)

        # Check if f_point1 and f_point2 have the same sign.
        return f_point1 * f_point2 > 0

    @staticmethod
    def pick_point_on_side(line: Line, side: Point, points: {Point}, same_side=True):
        for intersect in points:
            if same_side:
                if Construction.check_if_points_on_same_side(line, side, intersect):
                    return intersect
            else:
                if not Construction.check_if_points_on_same_side(line, side, intersect):
                    return intersect
        else:
            raise ValueError(f'No points were on the same side of {line} as point {side}')

    @staticmethod
    def pick_point_not_on_line(line: Line):
        """Pick a point not on the line for when we do not care about which side."""
        return line.point1 + line.get_perpendicular_at_point(line.point1).get_direction_vector()

    @staticmethod
    def pick_point_not_on_line_on_side(line: Line, side: Point, same_side=True):
        """Pick a point that is not on the line, but we do care which side."""
        point2 = line.point1 + line.get_perpendicular_at_point(line.point1).get_direction_vector()
        if Construction.check_if_points_on_same_side(line, side, point2) == same_side:
            return point2
        else:
            return line.point1 - line.get_perpendicular_at_point(line.point1).get_direction_vector()

    def EuclidI1(self, line: Line, side: Point, interesting=True) -> Point:
        """
        "To construct an equilateral triangle on a given finite straight line."
        Follows Euclid self of an equilateral triangle on a line segment. Returns the third point of the triangle.

        An extra point is required to specify which side of the line to construct the triangle. Euclid takes for granted
        that it can be done on either side, and does so on the top, without loss of generality.

        :param line: line upon which to construct the triangle. line's point1 and point2 should be vertices of triangle
        :param side: any point on the same side of line as the desired vertex
        :param interesting: bool representing whether or not to mark subsequent steps as interesting.
        :return: the point representing the third vertex of the equilateral triangle
        """
        if side in line:
            raise ValueError(f'Point {side} is on line {line}, so side is ambiguous when erecting triangle.')

        a, b = line.point1, line.point2
        # These are the steps of the constructions
        circ1 = self.add_circle(a, b, interesting=interesting)
        circ2 = self.add_circle(b, a, interesting=interesting)
        intersections = self.find_intersections(circ1, circ2)  # Only include circle intersections.
        c = None
        for intersect in intersections:
            if self.check_if_points_on_same_side(line, side, intersect):
                c = intersect
                self.add_line(a, intersect, interesting=interesting)
                self.add_line(b, intersect, interesting=interesting)
                break  # Only do it for one intersection point
        if c:
            return c
        else:
            raise ValueError(f'No intersections were on the same side of {line} as point {side}')

    ErectEquilateralTriangle = EuclidI1

    def EuclidI2(self, line_segment: Line, a: Point, interesting=True) -> Line:
        """
        To copy a segment.
        :param line_segment: Line segment to be copied
        :param a: the first point of the new, copied line segment
        :param interesting: bool representing whether or not to mark subsequent steps as interesting.
        :return: a new line whose point1 is a and point2 is the distance of line_segment away from a
        """
        # Choose b,c as the ends of the line segments.
        b, c = line_segment.point1, line_segment.point2
        # Occasionally, we can accidentally choose b = a.
        # Without loss of generality, choose b != a.
        if a == b:
            b, c = c, b
        ab = self.add_line(a, b, interesting=interesting)

        d = self.EuclidI1(ab, self.pick_point_not_on_line(ab))
        circle_bc = self.add_circle(b, c, interesting=interesting)
        intersections = self.find_intersections_line_circle(Line(d, b), circle_bc)
        g = self.pick_point_on_side(line_segment, d, intersections, same_side=False)
        circle_dg = self.add_circle(d, g, interesting=interesting)
        intersections = self.find_intersections_line_circle(Line(d, a), circle_dg)
        final_point = self.pick_point_on_side(ab, d, intersections, same_side=False)
        return self.add_line(a, final_point, interesting=interesting)

    CopySegment = EuclidI2

    def EuclidI3(self, short_line: Line, long_line: Line, interesting=True) -> Line:
        """
        To cut off a segment.
        :param short_line: the line whose point1 and point2 are the desired length apart
        :param long_line: the longer line from which we will cut the distance of short_line off
        :param interesting: bool representing whether or not to mark subsequent steps as interesting.
        :return: line equal to long_line, but whose point2 is a cut off to the appropriate length
        """
        if short_line not in self.lines or long_line not in self.lines:
            raise ValueError(f'Cannot cut off line segment. {short_line} or {long_line} not in {self}')
        a, b = long_line.point1, long_line.point2
        line_ad = self.EuclidI2(short_line, a, interesting=interesting)
        d = line_ad.point2
        circle_def = self.add_circle(center=a, point2=d, interesting=interesting)
        intersections = self.find_intersections_line_circle(long_line, circle_def)
        e = self.pick_point_on_side(Line(a, d), b, intersections)
        return Line(a, e)

    CutOffSegment = EuclidI3

    def EuclidI9(self, angle: Angle, interesting=True) -> Line:
        """
        To bisect an angle.
        :param angle: angle from which to bisect
        :param interesting: bool representing whether or not to mark subsequent steps as interesting.
        :return: the line that bisects angle
        """
        a = angle.vertex_point
        line1, line2 = angle.line1, angle.line2
        # pick an arbitrary point on line1 that is not a.
        d: Point = line1.point1 if line1.point1 != a else line1.point2
        # Cut off point E from line2 with length AD
        e = self.EuclidI3(short_line=Line(a, d), long_line=line2, interesting=interesting).point2
        # We need to pick a point opposite DE from A to show which side to erect the equilateral triangle.
        # Start at D, and walk in the direction of D-A.
        side: Point = 2 * d - a
        line_de = self.add_line(d, e, interesting=interesting)
        f = self.EuclidI1(line_de, side, interesting=interesting)
        return self.add_line(a, f, interesting=interesting)

    AngleBisector = EuclidI9

    def EuclidI10(self, line: Line, interesting=True) -> Point:
        """
        To bisect a given finite straight line.

        NOTE: This self is included in here as written in Elements for completion sake. Erecting a triangle and
        then bisecting the angle is effective, but slow when drawing every step. Use the perpendicular bisector instead.
        This self is given first to make the proof easier.
        :param line: line segment to be bisected
        :param interesting: bool representing whether or not to mark subsequent steps as interesting.
        :return: the midpoint of the line
        """
        a, b = line.point1, line.point2
        side = self.pick_point_not_on_line(line)  # We don't care which side to erect the triangle.
        c = self.EuclidI1(line, side, interesting=interesting)
        line_cb, line_ca = Line(c, b), Line(c, a)
        angle = Angle(line_cb, line_ca, c)
        perp_bisector = self.EuclidI9(angle, interesting=interesting)
        (intersections,) = self.find_intersections_line_line(line, perp_bisector)
        return intersections

    Midpoint = EuclidI10

    def PerpendicularBisector(self, line: Line, interesting=True) -> Line:
        """
        Erect the perpendicular bisector of a given line much faster.
        :param line: line segment to be bisected
        :param interesting: bool representing whether or not to mark subsequent steps as interesting.
        :return: the perpendicular bisector of line
        """
        a, b = line.point1, line.point2
        # These are the steps of the constructions
        circ1 = self.add_circle(a, b, interesting=interesting)
        circ2 = self.add_circle(b, a, interesting=interesting)
        intersections = self.find_intersections(circ1, circ2)  # Only include circle intersections.
        return self.add_line(*intersections, interesting=interesting)

    def EuclidI11(self, line: Line, point: Point, interesting=True) -> Line:
        """
        To draw a straight line at right angles to a given straight line from a given point on it.
        "To erect the perpendicular"

        :param line: the line of which the perpendicular will be erected
        :param point: point on line through which perpendicular should pass
        :param interesting: bool representing whether or not to mark subsequent steps as interesting.
        :return: the perpendicular to line passing through point
        """
        if point not in line:
            raise ValueError(f'Cannot erect a perpendicular. Point {point} is not on line {line}.')
        # rename point as c
        c = point
        # Pick an arbitrary point D on the line.
        d = line.point1 if line.point1 != point else line.point2
        # Make CE equal to CD.
        circle_center_c_radius_cd = self.add_circle(c, d, interesting=interesting)
        intersections = list(self.find_intersections_line_circle(line, circle_center_c_radius_cd))
        e = intersections[0] if intersections[0] != d else intersections[1]
        # Construct the equilateral triangle FDE on DE
        f = self.EuclidI1(Line(d, e), self.pick_point_not_on_line(line))
        # join CF
        return self.add_line(c, f, interesting=interesting)

    ErectPerpendicular = EuclidI11

    def EuclidI12(self, line: Line, point: Point, interesting=True) -> Line:
        """
        To draw a straight line perpendicular to a given infinite straight line from a given point not on it.
        "To drop a perpendicular"

        :param line: the line of which the perpendicular will be erected
        :param point: point not on line through which perpendicular should pass
        :param interesting: bool representing whether or not to mark subsequent steps as interesting.
        :return: the perpendicular to line passing through point
        """
        if point in line:
            raise ValueError(f'Cannot drop a perpendicular. Point {point} is on line {line}.')
        # rename point as C
        c = point
        # Pick a point on the opposite side of line from c
        d = self.pick_point_not_on_line_on_side(line, c, same_side=False)
        circle_center_c_radius_cd = self.add_circle(c, d, interesting=interesting)
        a, b = self.find_intersections_line_circle(line, circle_center_c_radius_cd)
        side = d
        f = self.ErectEquilateralTriangle(Line(a, b), side=side, interesting=interesting)
        return self.add_line(c, f)

    DropPerpendicular = EuclidI12

    def Perpendicular(self, line: Line, point: Point, interesting=True) -> Line:
        """
        Perpendicular to line through point. Will choose the proper self depending on if point is on the line or not

        :param line: the line of which the perpendicular will be erected
        :param point: point through which perpendicular should pass
        :param interesting: bool representing whether or not to mark subsequent steps as interesting.
        :return: the perpendicular to line passing through point
        """
        if point in line:
            return self.ErectPerpendicular(line, point, interesting=interesting)
        else:
            return self.DropPerpendicular(line, point, interesting=interesting)

    def EuclidI31(self, line: Line, point: Point, interesting=True) -> Line:
        """
        To draw a straight line through a given point parallel to a given straight line.


        :param line: the original line, whose parallel we will find
        :param point: point through which the parallel should pass
        :param interesting: bool representing whether or not to mark subsequent steps as interesting.
        :return: the parallel to line passing through point
        """
        if point in line:
            # If the point is already on the line, the parallel of the line is the line itself
            return line
        # rename point as A, points B,C on line
        a = point
        b, c = line.point1, line.point2
        circle_center_b_radius_ba = self.add_circle(b, a, interesting=interesting)
        intersections = self.find_intersections_line_circle(line, circle_center_b_radius_ba)
        d = list(intersections)[0]  # It doesn't matter which one we pick.
        circle_center_d_radius_da = self.add_circle(d, a, interesting=interesting)
        intersections = list(self.find_intersections_circle_circle(circle_center_b_radius_ba,
                                                                   circle_center_d_radius_da))
        e = intersections[0] if intersections[0] != a else intersections[1]  # Pick the intersection not A
        de = self.add_line(d, e, interesting=interesting)
        intersections = list(self.find_intersections_line_circle(de, circle_center_d_radius_da))
        f = intersections[0] if intersections[0] != e else intersections[1]
        return self.add_line(a, f, interesting=interesting)

    ParallelLine = EuclidI31
