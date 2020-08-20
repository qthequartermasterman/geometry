from Point import Point
from Line import Line
from Circle import Circle
from Construction import Construction
import copy
from decimal import Decimal
import math


def max_num_constructions(n):
    buffer = .5
    if n == 0:
        return 1
    elif n == 1:
        return 2 * buffer
    elif n == 2:
        return 24 * buffer
    elif n == 3:
        return 1344 * buffer
    elif n == 4:
        return 244608 * buffer
    else:
        return 250000 * buffer

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
    
const.add_random_construction(number_of_times=7)
const.draw_construction()
print(const)
'''

"""Square root"""
'''
num_to_take_sqrt = 1
with open('constructions/num_steps.csv', 'a+') as csv:
    while num_to_take_sqrt < 10000:
        # Initialize the construction
        max_num_steps = 2
        const = Construction()
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
                    filename = f'constructions/sqrt{num_to_take_sqrt}_construction_in_{max_num_steps}_steps'
                    const_copy.save_construction(filename, notes=check)
                    
                    #const_copy.draw_construction(filename)
                    #with open(f'{filename}.txt', 'a+') as f:
                    #    f.write(str(const_copy)+f'\n{check}\n\n')
                    print(const_copy)
                    break
                i += 1
            if check:
                csv.write(f'n for sqrt, {num_to_take_sqrt}, num steps, {max_num_steps}\n')
                break
            max_num_steps += 1
        num_to_take_sqrt += 1
'''

"""Square root given only one segment"""
'''
constructions_dict = {}

const = Construction()
a = Point(0, 0, 'A')
b = Point(1, 0, 'B')
const.points = {a, b}
ab = const.add_line(a, b, counts_as_step=False)

for num_steps in range(1, 5):
    for i in range(max_num_constructions(num_steps)):
        print(f'Steps: {num_steps}\tConstruction: {i}')
        const_copy = copy.deepcopy(const)
        const_copy.add_random_construction(number_of_times=num_steps)
        lengths_in_construction = const_copy.get_present_lengths()
        for length, points in lengths_in_construction.items():
            square = length**2
            square_int = int(square)
            if math.isclose(square_int, square):  # If the square of the length is close to an integer
                if square_int not in constructions_dict.keys():
                    constructions_dict[square_int] = (num_steps, points, const_copy)
sorted_constructions_dict = dict(sorted(constructions_dict.items()))
with open('num_steps.csv', 'w+') as csv:
    for n, tup in sorted_constructions_dict.items():
        csv.write(f'n for sqrt, {n}, num steps, {tup[0]}\n')
'''

"""Square root given a segment of length n"""
constructions_dict = {}

for num_to_take_sqrt in range(1, 100):
    const = Construction()
    a = Point(0, 0, 'A')
    b = Point(1, 0, 'B')
    c = Point(-num_to_take_sqrt, 0, 'C')
    const.points = {a, b, c}
    ab = const.add_line(a, b, counts_as_step=False)
    cb = const.add_line(c, b, counts_as_step=False)

    check = None

    for num_steps in range(1, 10):
        for i in range(max_num_constructions(num_steps)):
            print(f'sqrt(n) {num_to_take_sqrt}\tSteps: {num_steps}\tConstruction: {i}')
            const_copy = copy.deepcopy(const)
            const_copy.add_random_construction(number_of_times=num_steps)
            lengths_in_construction = const_copy.get_present_lengths()

            check = const_copy.check_lengths(Decimal.sqrt(Decimal(num_to_take_sqrt)))
            if check:
                print('FOUND ONE')
                filename = f'constructions_given_two_segments/sqrt{num_to_take_sqrt}_construction_in_{num_steps}_steps'
                const_copy.save_construction(filename, notes=check)
                constructions_dict[num_to_take_sqrt] = (num_steps, const_copy)
                print(const_copy)
                break
        if check:
            break

sorted_constructions_dict = dict(sorted(constructions_dict.items()))
with open('num_steps.csv', 'w+') as csv:
    for n, tup in sorted_constructions_dict.items():
        csv.write(f'n for sqrt, {n}, num steps, {tup[0]}\n')
