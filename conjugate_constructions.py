import networkx as nx
from Point import Point
from Construction import Construction
from Object import Object

const = Construction()

a = Point(0, 0, 'A')
b = Point(1, 0, 'B')
const.points.update({a, b})
circ1 = const.add_circle(a, b)
circ2 = const.add_circle(b, a)
intersections = const.points - {a, b}
for intersect in intersections:
    ac = const.add_line(a, intersect)
    bc = const.add_line(b, intersect)
    break  # Only do it for one intersection point
ab = const.add_line(a, b, counts_as_step=False)
const.draw_construction()
print(const)


def get_gap_code_to_describe_permutation_group(list_of_permutations: [int], group_name='group'):
    count = 0
    print(f'GAP Code for {group_name}')
    print(f'{group_name}:=Group(')
    for permutation in list_of_permutations:
        # Print this so I can copy paste it into GAP
        print(f'AsPermutation(Transformation({permutation})){"," if count < len(slist) - 1 else ");"}')
        count += 1
    print(f'StructureDescription(group);')
    print(f'Print("Did the permutations form a group?\t", Size({group_name})={len(list_of_permutations)}, "\\n");')


def save_permutations_to_file(list_of_permutations: [int], filename: str, object_dict: {Object: int}):
    with open(filename, 'w+') as f:
        for permutation in list_of_permutations:
            permutation = [str(x) for x in permutation]
            f.write(', '.join(permutation) + '\n')
        f.write('\n\n\n\nLegend:\n')
        for object, id in object_dict:
            f.write(f'{id}, {str(object)}')


_, slist = const.get_conjugate_constructions()
print(len(slist), '\n\n\n\n')
get_gap_code_to_describe_permutation_group(slist, 'EuclidI1')

