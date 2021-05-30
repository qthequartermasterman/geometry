import geometry.core
from geometry.core.Circle import Circle
from geometry import Construction
from geometry.core.EuclidConstructions import BaseConstruction
from geometry import Point
from geometry.core.Line import Line
from geometry import Object

import copy
import time
import pickle

from multiprocessing import Process, cpu_count #, Queue
from multiprocessing.managers import SyncManager
import multiprocessing.managers as managers
from queue import Empty, Queue

from typing import List

# Declare some constants
point_minimal: {Point: int} = {}  # Contain the minimal construction length of each new point
maximum_depth = 3  # How many steps deep can our search tree go?
#unique_constructions: {int, int} = {}  # Number of unique constructions of length.
construction_job_queue = Queue()  # Job queue. Holds the constructions to analyze next

# Keys are the visited constructions (which are added to queue),
# values are dummy, since multiprocessing managers only work with dicts
visited_dict: {Construction: int} = {}

# Directory to store all results
results_dir = '../../results/'


# Helper functions for our multiprocessing servers. These are not lambdas, since those are not pickle-able.
def return_queue(): return construction_job_queue


def return_point_minimal(): return point_minimal


def return_maximum_depth(): return maximum_depth


#def return_unique_construction(): return unique_constructions


def return_visited_dict(): return visited_dict


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


class QueueManager(SyncManager):
    """Custom multiprocessing manager subclassing SyncManager. Only difference is later we will register various
    custom methods for consistency across clients. """
    pass


def check_for_minimal_points(construction: Construction, most_recent_object: Object,
                             point_minimal_construction_dict: {Point, int}) -> None:
    """
    Check the given construction's new points. If the construction is a faster way of generating any point than what is
    stored in point_minimal_construction_dict, then record this one as a faster construction.

    :param construction: the current construction to analyze
    :param most_recent_object: most recent line or circle added to the construction, so we don't have to check all
    points--just the new ones
    :param point_minimal_construction_dict: dictionary to store all the data (as a side effect)
    :return: None
    """
    for point in construction.update_intersections_with_object(most_recent_object):
        if point not in point_minimal_construction_dict.keys():
            point_minimal_construction_dict[point] = len(construction)
            print('\033[31m New lowest', point, len(construction), '\033[0m')
        else:
            if point_minimal_construction_dict[point] > len(construction):
                point_minimal_construction_dict[point] = len(construction)
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
                check_for_minimal_points(new_construction, new_object, point_minimal_construction_dict)
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

        check_for_minimal_points(queue_construction, new_object, point_minimal)

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


def construct_bfs_parallel(queue: Queue, visited_dict: {}, point_minimal, maximum_depth, interesting=True):
    while not queue.empty():
        queue_construction, new_object = queue.get()
        print('\033[34m Dequeued:', len(queue_construction), new_object)

        if len(queue_construction) > maximum_depth:
            # If we are too deep, skip this one and move to the next one in queue
            continue

        check_for_minimal_points(queue_construction, new_object, point_minimal)

        for action in queue_construction.actions:
            new_construction = copy.deepcopy(queue_construction)
            new_object = new_construction.add_step_premade(action, interesting=interesting)
            #print(f'\033[36mCurrent Length: {len(queue_construction)}\t Number of actions {len(queue_construction.actions)}\tChecking {new_object}\033[0m')
            if new_construction not in visited_dict.keys():
                #print(f'\t\033[36mAdding {new_object} to discovery queue\033[0m')
                visited_dict[new_construction] = 1
                queue.put((new_construction, new_object))


def construct():
    # Define Construction
    construction = BaseConstruction()
    # Depth-first Search
    # construct_helper_dfs(construction, 0)

    # Breadth-first Search
    construct_bfs(construction, maximum_depth)
    print(point_minimal)


def construct_bfs_parallel_processes(job_queue: Queue, initialized_construction_dict: {Construction: int},
                                     point_minimal_construction_dict: {Point, int}, max_depth: int) -> [Process]:
    # Initialize processes. Each process will do construct_bfs_parallel.
    num_processes = cpu_count()  # We want to maximize the process count of each client in our cluster. Use every CPU!
    processes = [Process(target=construct_bfs_parallel,
                         args=(job_queue, initialized_construction_dict,
                               point_minimal_construction_dict, max_depth,))
                 for _ in range(num_processes)]
    # Start each process
    for process in processes:
        process.start()
    return processes


def make_server_manager(port, authkey):
    """Create a manager for the server, listening on the given port."""
    # Register the getter functions for queue, max depth, visited, etc...
    # We need to register these functions so that our client managers can use the shared state data.
    QueueManager.register('get_queue', return_queue)
    QueueManager.register('get_maximum_depth', return_maximum_depth)
    QueueManager.register('get_visited_dict', return_visited_dict, managers.DictProxy)
    #QueueManager.register('get_unique_constructions', return_unique_construction, managers.DictProxy)
    QueueManager.register('get_point_minimal', return_point_minimal, managers.DictProxy)

    # Create the server manager and start
    # Bind to all addresses, so address is empty string
    server_manager = QueueManager(address=('', port), authkey=authkey)
    server_manager.start()
    print(f'Server started at port {port}')
    return server_manager


def make_client_manager(ip, port, authkey):
    """Create a manager for a client"""
    # Register the getter functions for queue, max depth, visited, etc...
    # We need to register these functions so that our client managers can use the shared state data.
    QueueManager.register('get_queue')
    QueueManager.register('get_maximum_depth')
    QueueManager.register('get_visited_dict')
    #QueueManager.register('get_unique_constructions')
    QueueManager.register('get_point_minimal')
    client_manager = QueueManager(address=(ip, port), authkey=authkey)
    client_manager.connect()

    print(f'Client connected to {ip}:{port}')
    return client_manager


def run_client() -> [Process]:
    # Initialize and start the manager
    # client_manager = make_client_manager('192.168.254.19', 12349, b'1234')
    client_manager = make_client_manager('localhost', 12349, b'1234')

    # Get our shared data structures
    job_queue = client_manager.get_queue()
    point_minimal_construction_dict = client_manager.get_point_minimal()
    initialized_constructions_dict = client_manager.get_visited_dict()
    max_depth = client_manager.get_maximum_depth()._getvalue()

    # Initialize the procsesses and start running analysis
    processes = construct_bfs_parallel_processes(job_queue, initialized_constructions_dict,
                                                 point_minimal_construction_dict, max_depth)
    return processes


def print_report(point_minimal_length_dict: {Point: int}, unique_constructions_dict: {int: int},
                 generated_constructions: List[Construction]):
    # Perform our final report
    print(f'\033[32mMinimal Construction of Points at {time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())}')
    print(f'\tDiscovered {len(point_minimal)} constructed points\033[0m')
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


def run_bfs_in_parallel():
    manager = make_server_manager(12349, b'1234')
    # Reference the shared queues and dicts.
    construction_job_queue = manager.get_queue()
    point_minimal = manager.get_point_minimal()
    visited_dict = manager.get_visited_dict()
    maximum_depth = manager.get_maximum_depth()

    # Define Construction
    base_construction = BaseConstruction()
    construction_job_queue.put((base_construction, tuple(base_construction.points)[0]))

    run_client()

    # Set up the loop that will wait and print progress until completed
    start_time = time.time()
    most_recent_time = time.time()
    last_print_time = time.time()
    empty = construction_job_queue.empty()

    cut_off_time = 5 * 60 * 60  # 5 hr = 5 * 60 min/hr * 60 sec/min

    while most_recent_time - start_time <= cut_off_time:
        if most_recent_time - last_print_time > 2:
            unique_constructions = count_unique_constructions(visited_dict.keys())
            print_report(point_minimal, unique_constructions, visited_dict.keys())
            if empty and construction_job_queue.empty():
                # If the queue is empty and has been for 2 seconds, go ahead and cancel it, since I can't find a
                # cleaner way of stopping.
                break
            else:
                empty = construction_job_queue.empty()

            last_print_time = time.time()
        most_recent_time = time.time()

    # Perform our final report
    # Minimal Construction Length for each point
    point_minimal = dict(point_minimal)
    # Number of unique constructions of each length (categorized)
    unique_constructions = count_unique_constructions(visited_dict.keys())
    # Total number of unique constructions generated (not necessarily categorized by length)
    generated_construction_list = list(visited_dict.keys())

    print_report(point_minimal, unique_constructions, generated_construction_list)

    # Save the generated list to disc.
    with open(results_dir + 'visited_constructions.pkl', 'wb') as visited_constructions_file:
        pickle.dump(generated_construction_list, visited_constructions_file)

    # Save the job queue (for future analysis)
    try:
        with open(results_dir + 'queue.pkl', 'wb') as construction_queue_file:
            pickle.dump(construction_job_queue._getvalue(), construction_queue_file)
    except:
        pass

    # Empty the job queue
    item = True
    while item:
        try:
            item = construction_job_queue.get(block=False)
        except Empty:
            break

    time.sleep(2)
    manager.shutdown()


def run_bfs_in_series(queue, visited_dict, point_minimal, maximum_depth):
    base_construction = BaseConstruction()
    visited_dict[base_construction] = 0  # Put the base construction in our visited_dict
    construction_job_queue.put((base_construction, tuple(base_construction.points)[0]))
    construct_bfs_parallel(queue, visited_dict, point_minimal, maximum_depth)
    # Perform our final report
    # Minimal Construction Length for each point
    point_minimal = dict(point_minimal)

    # Number of unique constructions of each length (categorized)
    unique_constructions = count_unique_constructions(visited_dict.keys())

    # Total number of unique constructions generated (not necessarily categorized by length)
    generated_construction_list = list(visited_dict.keys())

    print_report(point_minimal, unique_constructions, generated_construction_list)


if __name__ == '__main__':

    """import timeit

    t = timeit.Timer(
        lambda: run_bfs_in_series(construction_job_queue, visited_dict, unique_constructions, point_minimal,
                                  maximum_depth))
    print(t.timeit(5))"""

    run_bfs_in_series(construction_job_queue, visited_dict, point_minimal, maximum_depth)
    #run_bfs_in_parallel()