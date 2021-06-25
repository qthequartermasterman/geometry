import geometry.core
from geometry.core.Circle import Circle
from geometry import Construction
from geometry.core.EuclidConstructions import base_construction
from geometry import Point
from geometry.core.Line import Line
from geometry import Object
from geometry.core.Construction import ConstructionMode

import copy
import time
from queue import Queue
from typing import List

# Declare some constants
point_minimal_construction_length: {Point: int} = {}  # Contain the minimal construction length of each new point
maximum_depth = 3  # How many steps deep can our search tree go?
construction_job_queue = Queue()  # Job queue. Holds the constructions to analyze next

# Keys are the generated constructions (which are added to queue),
# values are dummy, since multiprocessing managers only work with dicts
generated_constructions: {Construction: int} = {}

# Directory to store all results
results_dir = '../../../results/'


def count_unique_constructions(constructions_set):
    """
    Counts the number of unique constructions of every length in the given constructions set.
    :param constructions_set: set containing all of the visited constructions
    :return:
    """
    length_num_unique_dict = {}

    for construction in constructions_set:
        length = len(construction)
        if length in length_num_unique_dict.keys():
            length_num_unique_dict[length] += 1
        else:
            length_num_unique_dict[length] = 1

    return length_num_unique_dict


def check_for_minimal_points(construction: Construction, most_recent_object: Object,
                             point_minimal_construction_dict: {Point, int}, verbose=False) -> None:
    """
    Check the given construction's new points. If the construction is a faster way of generating any point than what is
    stored in point_minimal_construction_dict, then record this one as a faster construction.


    :param construction: the current construction to analyze
    :param most_recent_object: most recent line or circle added to the construction, so we don't have to check all
    points--just the new ones
    :param point_minimal_construction_dict: dictionary to store all the data (as a side effect)
    :param verbose: Bool representing whether diagnostic information should be printed to console
    :return: None
    """
    for point in construction.update_intersections_with_object(most_recent_object):
        if point not in point_minimal_construction_dict.keys():
            point_minimal_construction_dict[point] = len(construction)
            if verbose:
                print('\033[31m New lowest', point, len(construction), '\033[0m')
        else:
            if point_minimal_construction_dict[point] > len(construction):
                point_minimal_construction_dict[point] = len(construction)
                if verbose:
                    print('\033[31m New lowest', point, len(construction), '\033[0m')


def construct_helper_dfs(construction: Construction, point_minimal_construction_dict: {Point, int}, max_depth: int,
                         current_depth: int, interesting=True) -> None:
    """
    Performs a recursive, serial depth-first search for points.

    Takes the given construction, and for each possible action (i.e. pick every two distinct points then either draw a
    line or a circle), checks if the action already exists, and if not checks if that is a shorter construction than
    the previously stored minimal construction. After all that processing, recursively calls the function on the newly
    created construction.


    :param construction: the current construction to analyze
    :param point_minimal_construction_dict: {Point, int} dictionary with points as keys and the current shortest
    construction length as values
    :param max_depth: maximum depth for search. Will terminate the branch if maximum depth is achieved.
    :param current_depth: current depth of this node on search tree
    :param interesting: should mark the newly constructed points as interesting in the Construction? Defaults to true
    :return: None
    """

    if current_depth >= max_depth:
        return

    # For every construction, we pick all pairwise distinct points, then either draw a line, circle with center point1,
    # or circle with center point2
    for point1 in construction.points:
        for point2 in construction.points - {point1}:
            for action in range(2):
                # Make a copy of the construction, so we can use the old one for the next branch
                new_construction = copy.deepcopy(construction)
                # Perform the action
                if action == 0:
                    # Draw a line
                    action = new_construction.add_line
                    new_object = action(point1, point2, interesting)
                elif action == 1:
                    # Draw circle with center point1 radius point1-point2
                    action = new_construction.add_circle
                    new_object = action(point1, point2, interesting)
                else:
                    # Draw circle with center point2 radius point1-point2
                    action = new_construction.add_circle
                    new_object = action(point2, point1, interesting)

                # Check if new_object has already been built.
                if new_object in construction.steps:
                    break

                # Check if the new construction is a faster way of generating any points
                check_for_minimal_points(new_construction, new_object, point_minimal_construction_dict, False)
                # Recursively call this function on the new construction
                construct_helper_dfs(new_construction, point_minimal_construction_dict, max_depth,
                                     current_depth + 1, interesting)


def construct_bfs(construction: Construction, max_depth: int, interesting=True):
    visited = set()
    queue = []

    visited.add(construction)
    queue.append((construction, tuple(construction.points)[0]))

    while queue:
        queue_construction, new_object = queue.pop(0)
        print('Dequeued:', len(queue_construction), new_object)

        if len(queue_construction) > max_depth:
            # If we are too deep, skip this one and move to the next one in queue
            continue

        check_for_minimal_points(queue_construction, new_object, point_minimal_construction_length, False)

        prebuilt_steps = queue_construction.steps[:]
        for point1 in queue_construction.points:
            for point2 in queue_construction.points - {point1}:
                for action in range(2):
                    new_construction = copy.deepcopy(queue_construction)
                    action = new_construction.add_circle if action else new_construction.add_line
                    new_object = action(point1, point2, interesting)
                    if new_construction not in visited:
                        visited.add(new_construction)
                        if new_object not in prebuilt_steps:
                            queue.append((new_construction, new_object))


def print_report(point_minimal_length_dict: {Point: int}, unique_constructions_dict: {int: int},
                 generated_constructions: List[Construction]):
    # Perform our final report
    print(f'\033[32mMinimal Construction of Points at {time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())}')
    print(f'\tDiscovered {len(point_minimal_construction_length)} constructed points\033[0m')
    # Minimal Construction Length for each point
    print('\033[32mMinimal Construction Length for each point:')
    for point, length in point_minimal_length_dict.items():
        print('\t\033[32m', length, point)

    # Number of unique constructions of each length (categorized)
    print('\033[33mNumber of Unique Constructions of each given length')
    for num_steps, num_constructions in unique_constructions_dict.items():
        print('\tSteps:', num_steps, 'Num Unique Constructions: ', num_constructions)

    # Total number of unique constructions generated (not necessarily categorized by length)
    print('\033[34mTotal Unique Constructions')
    print(f'\tGenerated {len(generated_constructions)} different constructions')

    # Reset colors
    print('\033[0m')


def generate_constructions_breadth_first_search(queue: Queue, generated_constructions_dict: {Construction: int},
                                                point_minimal_construction_length_dict: {Point: int},
                                                max_search_depth: int,
                                                interesting=True, verbose=False):
    """
    Runs a breadth-first-search for new points and constructions from the base construction.
    :param queue: Queue that holds the constructions that we need to build off of.
    :param generated_constructions_dict: Dictionary whose keys are previously generated constructions and
    values are ints. This should logically be a set, but since multiprocess does not have a shared set, we can make due
    by using the keys of this dictionary, instead.
    :param point_minimal_construction_length_dict: Dictionary whose keys are points and values are the lengths of corresponding
    minimal constructions (found so far)
    :param max_search_depth: Maximum depth to search. If a construction is deeper than this, skip.
    :param interesting: Bool representing whether or not constructed objects should be marked interesting
    :param verbose: Bool representing whether or not to include diagnostic information
    :return:
    """
    while not queue.empty():
        queue_construction, new_object = queue.get()
        if verbose:
            print('\033[34m Dequeued:', len(queue_construction), new_object)
        if len(queue_construction) > max_search_depth:
            # If we are too deep, skip this one and move to the next one in queue
            continue
        # Check to see if we have any faster constructions
        check_for_minimal_points(queue_construction, new_object, point_minimal_construction_length_dict, verbose=False)

        # Generate the new child constructions for the current construction and enqueue them for later checking
        for action in queue_construction.actions:
            new_construction = copy.deepcopy(queue_construction)
            new_object = new_construction.add_step_premade(action, interesting=interesting)
            if verbose:
                print('\033[36m', 'Generating new construction: '
                      f'Current Length: {len(queue_construction)}',
                      f'Number of actions {len(queue_construction.actions)}',
                      f'Checking {new_object}',
                      '\033[0m')
            if new_construction not in generated_constructions_dict.keys():
                if verbose:
                    print(f'\t\033[36mAdding {new_object} to discovery queue\033[0m')
                generated_constructions_dict[new_construction] = 1
                queue.put((new_construction, new_object))


def run_bfs_in_series(queue: Queue, previously_generated_constructions_dict: {Construction: int},
                      point_minimal_construction_dict: {Point, int}, max_search_depth: int, verbose=False,
                      report=True, construction_mode=ConstructionMode.DEFAULT) -> None:
    """
    Runs a breadth-first-search for new points and constructions from the base construction.
    NOTE: This is a serial Breadth-first search. A parallelized version of this search exists in the server file.

    :param queue: Queue that holds the constructions that we need to build off of.
    :param previously_generated_constructions_dict: Dictionary whose keys are previously generated constructions and
    values are ints. This should logically be a set, but since multiprocess does not have a shared set, we can make due
    by using the keys of this dictionary, instead.
    :param point_minimal_construction_dict: Dictionary whose keys are points and values are the lengths of corresponding
    minimal constructions (found so far)
    :param max_search_depth: maximum number of steps to permit in a generated construction
    :param verbose: Bool representing whether or not we should print reports
    :return: None
    """

    base_construction = base_construction(construction_mode=construction_mode)
    previously_generated_constructions_dict[base_construction] = 0  # Put the base construction in our visited_dict
    queue.put((base_construction, tuple(base_construction.points)[0]))
    generate_constructions_breadth_first_search(queue, previously_generated_constructions_dict,
                                                point_minimal_construction_dict,
                                                max_search_depth, verbose=verbose)
    # Perform our final report
    # Minimal Construction Length for each point
    point_minimal_construction_dict = dict(point_minimal_construction_dict)

    # Number of unique constructions of each length (categorized)
    unique_constructions = count_unique_constructions(previously_generated_constructions_dict.keys())

    # Total number of unique constructions generated (not necessarily categorized by length)
    generated_construction_list = list(previously_generated_constructions_dict.keys())

    if report:
        print_report(point_minimal_construction_dict, unique_constructions, generated_construction_list)


def find_all_constructions_of_length(max_depth: int, verbose=False, report=True,construction_mode=ConstructionMode.DEFAULT):
    # Declare some constants
    point_minimal_construction_length_dict: {Point: int} = {}  # Contain the minimal construction length of each new point
    construction_queue = Queue()  # Job queue. Holds the constructions to analyze next

    # Keys are the generated constructions (which are added to queue),
    # values are dummy, since multiprocessing managers only work with dicts
    generated_constructions_dict: {Construction: int} = {}
    run_bfs_in_series(construction_queue, generated_constructions_dict, point_minimal_construction_length_dict, max_depth, verbose, report,construction_mode=construction_mode)


if __name__ == '__main__':
    #run_bfs_in_series(construction_job_queue, generated_constructions, point_minimal_construction_length, maximum_depth)
    #find_all_constructions_of_length(maximum_depth)
    find_all_constructions_of_length(3, verbose=True, construction_mode=ConstructionMode.DEFAULT)
    find_all_constructions_of_length(3, verbose=True, construction_mode=ConstructionMode.LINES_ONLY)
    find_all_constructions_of_length(3, verbose=True, construction_mode=ConstructionMode.CIRCLES_ONLY)