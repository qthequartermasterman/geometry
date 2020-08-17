import math

class Point:
    def __init__(self, x: float, y: float, name: str = ''):
        self.x = x
        self.y = y
        self.name = name

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __sub__(self, other):
        return Point(self.x-other.x, self.y-other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        if type(other) in (float, int):  # Take the scalar Product
            return Point(other*self.x, other*self.y)
        elif type(other) is Point:  # Take the dot product
            return self.x*other.x + self.y*other.y
        else:
            print(f'invalid multiplication of {self} and {other}')

    def __rmul__(self, other):
        return self.__mul__(other)

    def __abs__(self):
        return math.sqrt(self * self)

    def __repr__(self):
        return f'Point {self.name}: ({self.x}, {self.y})'

    def __hash__(self):
        return hash(repr(self))


class Line:
    def __init__(self, point1: Point, point2: Point):
        self.point1 = point1
        self.point2 = point2
        self.slope = self.calculate_slope(point1, point2)
        self.intercept = self.calculate_intercept(point1, point2, self.slope)

    @staticmethod
    def calculate_slope(point1: Point, point2: Point):
        return float(point2.y-point1.y)/float(point2.x-point1.x)

    def calculate_intercept(self, point1: Point, point2: Point, slope=None):
        if slope is None:
            slope = self.calculate_slope(point1, point2)
        else:
            slope = slope
        return point1.x * slope


class Circle:
    def __init__(self, center: Point, radius: float):
        self.center = center
        self.radius = radius


class Construction:
    def __init__(self):
        pass

    def find_intersections(self, object1, object2) -> {Point}:
        if type(object1) is Line:
            if type(object2) is Line:
                return self.find_intersections_line_line(object1, object2)
            elif type(object2) is Circle:
                return self.find_intersections_line_circle(object1, object2)
        elif type(object2) is Circle:
            if type(object1) is Line:
                return self.find_intersections_line_circle(object1, object2)
            elif type(object1) is Circle:
                return self.find_intersections_circle_circle(object1, object2)
        print('Cannot find intersection of unsupported objects')
        return None

    @staticmethod
    def find_intersections_line_line(line1: Line, line2: Line) -> {Point}:
        """ In the Euclidean plane, two lines can intersect at most once (by Postulate 5/Playfair's Axiom)
            Consequently, this method returns either the empty set (if the lines are parallel/coinciding) or a set
            with one point (if they intersect).

            :param line1
            :param line2

            :returns {Point} a set of at most one point representing the intersection of the two lines
        """
        if line1.slope != line2.slope:  # Different slopes guarantees intersection (by Postulate 5)
            x = (line2.intercept - line1.intercept)/(line1.slope-line2.slope)
            y = line1.slope * x + line1.intercept
            return {Point(x, y)}
        else:  # Parallel or coinciding -> no intersection
            return {}

    @staticmethod
    def find_intersections_line_circle(line, circle) -> {Point}:
        """ In the Euclidean plane, two lines can intersect at most once (by Postulate 5/Playfair's Axiom)
            Consequently, this method returns either the empty set (if the lines are parallel/coinciding) or a set
            with one point (if they intersect).

            :param line1
            :param line2

            :returns {Point} a set of at most one point representing the intersection of the two lines
        """
        # We can represent our line as all vectors p so that p = p1+t(p2-p1) where p1, p2 are our original points
        line_basis_vector = line.point2-line.point1
        # Circle is all points p so that |p-c|=r where c is the center
        # substiting the original line equation in for the circle equation, we get a quadratic equation
        # at^2+bt+c=0 where:
        a = line_basis_vector * line_basis_vector  # Dot product
        b = line_basis_vector * (line.point1-circle.center) * 2
        c = line.point1 * line.point1 + circle.center * circle.center - (line.point1*circle.center)*2 - circle.radius**2

        discriminant = b**2 - 4*a*c
        if discriminant < 0:  # There are no real solutions, so the line and circle do not intersect on the plane
            return {}
        elif discriminant == 0:  # The line is tangent and there is one real solution
            t_solution = -b/(2*a)
            point_solution = line.point1 + line_basis_vector * t_solution
            return {point_solution}
        else:  # The discriminant is positive, so there are two real solutions and the line is secant
            t_solution1 = (-b + math.sqrt(discriminant)) / (2 * a)
            t_solution2 = (-b - math.sqrt(discriminant)) / (2 * a)
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
        elif distance_between_centers < abs(r1-r2):  # One circle contained in other
            return {}
        elif distance_between_centers == 0:  # Circles have same center and are either coincident or the other is contained within the one
            return {}
        else:
            dis_to_area_center = (r1**2 - r2**2 + distance_between_centers**2) / (2 * distance_between_centers)
            center_of_intersection_area = center1 + dis_to_area_center * diff_between_centers * (
                        1 / distance_between_centers)
            if dis_to_area_center == r1:  # The two circles are tangent and thus intersect at exactly one point
                return {center_of_intersection_area}
            else:  # Two circles intersect at two points
                height = math.sqrt(r1**2 - dis_to_area_center**2)
                x2 = center_of_intersection_area.x
                y2 = center_of_intersection_area.y
                x3 = x2 + height * (center2.y-center1.y) * (1/distance_between_centers)
                y3 = y2 - height * (center2.x - center1.x) * (1/distance_between_centers)
                x4 = x2 - height * (center2.y - center1.y) * (1 / distance_between_centers)
                y4 = y2 + height * (center2.x - center1.x) * (1 / distance_between_centers)
                return {Point(x3, y3), Point(x4, y4)}


