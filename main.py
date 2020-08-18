from Point import Point
from Line import Line
from Circle import Circle
from Construction import Construction

a = Point(0, 0, 'A')
b = Point(2, 0, 'B')
c = Point(3, 3, 'C')

ab = Line(a, b)
bc = Line(b, c)
ac = Line(a, c)

cAr2 = Circle(a, 2)
cBr2 = Circle(b, 2)
cCr2 = Circle(c, 2)

const = Construction()
const.points.update({a, b, c})
const.lines.update({ab, bc, ac})
const.circles.update({cAr2, cBr2, cCr2})
const.find_intersections(cAr2, cBr2)
const.find_intersections(cAr2, ac)
const.add_random_construction(number_of_times=10)
const.draw_construction()