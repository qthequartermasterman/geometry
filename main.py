from Point import Point
from Line import Line
from Circle import Circle
from Construction import Construction
import copy
from decimal import Decimal


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
'''
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
'''

"""Square root"""
num_to_take_sqrt = 1
with open('constructions/num_steps.csv', 'a+') as csv:
    while num_to_take_sqrt < 10000:
        # Initialize the construction
        max_num_steps = 2
        a = Point(0, 0, 'A')
        b = Point(1, 0, 'B')
        c = Point(-num_to_take_sqrt, 0, 'C')
        const.points = {a, b, c}
        ab = const.add_line(a, b, counts_as_step=False)
        cb = const.add_line(c, b, counts_as_step=False)

        while max_num_steps < 30:
            i = 0
            check = False
            while i < 100000:
                print(f'sqrt(n) {num_to_take_sqrt}\tsteps {max_num_steps}\tTrying {i}')
                const_copy = copy.deepcopy(const)
                const_copy.add_random_construction(number_of_times=max_num_steps)
                check = const_copy.check_lengths(Decimal.sqrt(Decimal(num_to_take_sqrt)))
                if check:
                    print('FOUND ONE')
                    filename = f'constructions/sqrt{num_to_take_sqrt}_construction_in_{max_num_steps}_steps.png'
                    const_copy.draw_construction(filename)
                    with open(f'sqrt{num_to_take_sqrt}_construction_in_{max_num_steps}_steps.txt', 'a+') as f:
                        f.write(str(const_copy)+f'{check}\n\n')
                    print(const_copy)
                    break
                i += 1
            if check:
                csv.write(f'n for sqrt, {num_to_take_sqrt}, num steps, {max_num_steps}\n')
                break
            max_num_steps += 1
        num_to_take_sqrt += 1

#const.add_random_construction(number_of_times=7)
#const.draw_construction()
#print(const)