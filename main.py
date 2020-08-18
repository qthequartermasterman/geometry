from Point import Point
from Line import Line
from Circle import Circle
from Construction import Construction


const = Construction()
'''
a = Point(0, 0, 'A')
b = Point(2, 0, 'B')
c = Point(3, 3, 'C')
const.points.update({a, b, c})

#const.lines.update({ab, bc, ac})
ab = const.add_line(a, b, counts_as_step=False)  # Line(a, b)
bc = const.add_line(b, c, counts_as_step=False)  # Line(b, c)
ac = const.add_line(a, c, counts_as_step=False)  # Line(a, c)

#const.circles.update({cAr2, cBr2, cCr2})
cAr2 = const.add_circle(a, b, counts_as_step=False)
cBr2 = const.add_circle(c, b, counts_as_step=False)
cCr2 = const.add_circle(a, c, counts_as_step=False)

const.add_random_construction(number_of_times=10)
'''

"""Euclid I.1"""
a = Point(0, 0, 'A')
b = Point(1, 0, 'B')
const.points.update({a, b})
ab = const.add_line(a, b, counts_as_step=False)
circ1 = const.add_circle(a, b)
circ2 = const.add_circle(b, a)
intersections = const.find_intersections(circ1, circ2)
for intersect in intersections:
    intersect.name += "intersection"
    print(intersect)
    const.add_line(a, intersect)
    const.add_line(b, intersect)

list_points = list(const.points)
list_int = list(intersections)

const.draw_construction()
print(const)