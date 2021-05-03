from geometry.core.Object import Object
from geometry.core.EuclidConstructions import RandomConstruction

from sympy.combinatorics import Permutation
from sympy.combinatorics.perm_groups import PermutationGroup
import networkx as nx
import matplotlib.pyplot as plt


def get_gap_code_to_describe_permutation_group(list_of_permutations: [int], group_name='group'):
    count = 0
    print(f'GAP Code for {group_name}')
    print(f'{group_name}:=Group(')
    for permutation in list_of_permutations:
        # Print this so I can copy paste it into GAP
        print(f'AsPermutation(Transformation({permutation})){"," if count < len(slist) - 1 else ");"}')
        count += 1
    print(f'StructureDescription({group_name});')
    print(f'Print("Did the permutations form a group?\t", Size({group_name})={len(list_of_permutations)}, "\\n");')


def save_permutations_to_file(list_of_permutations: [[int]], filename: str, object_dict: {Object: int}):
    with open(filename, 'w+') as f:
        for permutation in list_of_permutations:
            permutation = [str(x) for x in permutation]
            f.write(', '.join(permutation) + '\n')
        f.write('\n\n\n\nLegend:\n')
        for object, id in object_dict:
            f.write(f'{id}, {str(object)}')


def get_sympy_permutations_instances(list_of_permutations: [[int]]):
    sympy_list = [Permutation(perm) for perm in list_of_permutations]
    return sympy_list


def do_conjugate_constructions_form_group(sympy_permutations:[Permutation], verbose=False):
    symmetry_group = PermutationGroup(*sympy_permutations)
    order = symmetry_group.order()
    if verbose:
        print(f'The order of the conjugate construction group is {order}')
    if order != len(sympy_permutations):
        return False
    else:
        # This is working off the assumption that if sympy_permutations is all the elements,
        # then the group it generates will be the same size.
        return True


num_rand_constructions = 100
num_grouped_constructions = 0
size_of_construction = 5

for i in range(num_rand_constructions):
    print(f'\nTrying random construction number {i}')
    const = RandomConstruction(size_of_construction)

    _, slist = const.get_conjugate_constructions(zero_index=True)

    symlist = get_sympy_permutations_instances(slist)
    diagram_group = PermutationGroup(*symlist)
    form_group_bool = do_conjugate_constructions_form_group(symlist, True)
    print('Do conjugate constructions form a group?\t', form_group_bool)
    if form_group_bool:
        num_grouped_constructions += 1
        #print(symlist)
        #const.draw_construction()
        plt.title(f'Construction {i} has Topologial sorts that form a group of order {len(symlist)}')
        _, graph = const.get_dependency_graph(True)
        pos = nx.spiral_layout(graph)
        nx.draw_networkx(graph, pos)
        plt.show()
        plt.clf()
        #_, graph = const.get_dependency_graph(True)
        #adj = nx.adjacency_matrix(graph).toarray()
        #characteristic_polynomial = np.poly(adj)
    else:
        plt.title(f'Construction {i} has topologial sorts that do NOT form a group.\n They generate a group of order {diagram_group.order()}')
        _, graph = const.get_dependency_graph(True)
        pos = nx.kamada_kawai_layout(graph)
        nx.draw_networkx(graph, pos)
        plt.show()
        plt.clf()
    print(f'{num_grouped_constructions}/{i+1} = {num_grouped_constructions/(i+1) }had conjugate that formed groups')

print(f'{num_grouped_constructions}/{num_rand_constructions} had conjugates that formed groups')