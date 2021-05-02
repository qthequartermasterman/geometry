from Construction import Construction
from Point import Point
from Circle import Circle
from Line import Line
import copy
from main import num_random_constructions
import random
import time

import pickle

from multiprocessing import Process, Queue, Array, cpu_count
from multiprocessing.managers import SyncManager
import multiprocessing.managers as managers
from queue import Empty

# Contain the minimal construction length of each new point
point_minimal: {Point: int} = {}
maximum_depth = 4
unique_constructions: {int, int} = {}  # Number of unique constructions of length.
visited_dict: {Point: int} = {}
queue = Queue()


def return_queue(): return queue
def return_point_minimal(): return point_minimal
def return_maximum_depth(): return maximum_depth
def return_unique_construction(): return unique_constructions
def return_visited_dict(): return visited_dict


class QueueManager(SyncManager):
    pass


class BaseConstruction(Construction):
    def __init__(self):
        super().__init__()
        a = Point(0, 0, 'A')
        b = Point(1, 0, 'B')
        self.points = {a, b}
        self.actions = self.get_valid_actions({a, b}, True)


def construct_helper_dfs(construction, depth, interesting=True):
    if depth == maximum_depth:
        return

    prebuilt_steps = construction.steps[:]
    for point1 in construction.points:
        for point2 in construction.points - {point1}:
            for action in range(2):
                new_construction = copy.deepcopy(construction)
                action = new_construction.add_circle if action else new_construction.add_line
                new_object = action(point1, point2, interesting)
                if new_object in prebuilt_steps:
                    break

                for point in new_construction.update_intersections_with_object(new_object):
                    if point not in point_minimal.keys():
                        point_minimal[point] = len(new_construction)
                    else:
                        if point_minimal[point] > len(new_construction):
                            point_minimal[point] = len(new_construction)
                            print(point, len(new_construction))

                construct_helper_dfs(new_construction, depth + 1, interesting)


def construct_bfs(construction, maximum_depth, interesting=True):
    visited = set()
    queue = []

    visited.add(construction)
    queue.append((construction, tuple(construction.points)[0]))

    while queue:
        queue_construction, new_object = queue.pop(0)
        print('Dequeued:', len(queue_construction), new_object)

        # Count the number of constructions while we go
        if len(queue_construction) in unique_constructions.keys():
            unique_constructions[len(queue_construction)] += 1
        else:
            unique_constructions[len(queue_construction)] = 1

        if len(queue_construction) > maximum_depth:
            # If we are too deep, skip this one and move to the next one in queue
            continue

        for point in queue_construction.update_intersections_with_object(new_object):
            if point not in point_minimal.keys():
                point_minimal[point] = len(queue_construction)
            else:
                if point_minimal[point] > len(queue_construction):
                    point_minimal[point] = len(queue_construction)
                    print(point, len(queue_construction))

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


def construct_bfs_parallel(queue: Queue, visited_dict: {}, unique_constructions: {}, point_minimal, maximum_depth,
                           interesting=True):
    while queue:
        queue_construction, new_object = queue.get()
        print('\033[34m Dequeued:', len(queue_construction), new_object)

        # Count the number of constructions while we go
        if len(queue_construction) in unique_constructions.keys():
            unique_constructions[len(queue_construction)] += 1
        else:
            unique_constructions[len(queue_construction)] = 1
        if len(queue_construction) > maximum_depth:
            # If we are too deep, skip this one and move to the next one in queue
            continue

        for point in queue_construction.update_intersections_with_object(new_object):
            if point not in point_minimal.keys():
                point_minimal[point] = len(queue_construction)
                print('\033[31m New lowest', point, len(queue_construction))
            else:
                if point_minimal[point] > len(queue_construction):
                    point_minimal[point] = len(queue_construction)
                    print('\033[31m New lowest', point, len(queue_construction))
        """
        used_points = set()
        for point1 in queue_construction.points:
            used_points.add(point1)
            for point2 in queue_construction.points - used_points:
                for action in range(3):
                    new_construction = copy.deepcopy(queue_construction)
                    prebuilt_steps = new_construction.steps[:]
                    #action = new_construction.add_circle if action else new_construction.add_line
                    #new_object = action(point1, point2, interesting)
                    if action == 0:
                        new_object = new_construction.add_line(point1, point2, interesting)
                    elif action == 1:
                        new_object = new_construction.add_circle(point1, point2, interesting)
                    else:
                        new_object = new_construction.add_circle(point2, point1, interesting)

                    if new_construction not in visited_dict.keys():
                        visited_dict[new_construction] = 1
                        if new_object not in prebuilt_steps:
                            queue.put((new_construction, new_object))
        """

        for action in queue_construction.actions:
            new_construction = copy.deepcopy(queue_construction)
            if isinstance(action, Circle):
                action_function = new_construction.add_circle
                point1 = new_construction.find_point(action.center)
                point2 = new_construction.find_point(action.point2)
            elif isinstance(action, Line):
                action_function = new_construction.add_line
                point1 = new_construction.find_point(action.point1)
                point2 = new_construction.find_point(action.point2)
            else:
                raise TypeError(f'Invalid action type {action}')
            if point1 is None or point2 is None:

                raise TypeError(f'Point does not exist {point1} {point2}\n{action.point2}\n{new_construction.points}')
            new_object = action_function(point1, point2, interesting)
            print(f'\033[36mChecking {new_object}\033[0m')
            if new_construction not in visited_dict.keys():
                print(f'\t\033[36mAdding {new_object} to discovery queue\033[0m')
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
    print(unique_constructions)


def construct_bfs_parallel_processes(queue, visited_dict, unique_constructions, point_minimal, maximum_depth):


    # Initialize processes
    import os
    #num_processes = len(os.sched_getaffinity(0))
    num_processes = cpu_count()
    processes = [Process(target=construct_bfs_parallel,
                         args=(queue, visited_dict, unique_constructions, point_minimal, maximum_depth,))
                 for _ in range(num_processes)]
    for process in processes:
        process.start()


def make_server_manager(port, authkey):
    """Create a manager for the server, listening on the given port."""
    QueueManager.register('get_queue', return_queue)
    QueueManager.register('get_maximum_depth', return_maximum_depth)
    QueueManager.register('get_visited_dict', return_visited_dict, managers.DictProxy)
    QueueManager.register('get_unique_constructions', return_unique_construction, managers.DictProxy)
    QueueManager.register('get_point_minimal', return_point_minimal, managers.DictProxy)


    manager = QueueManager(address=('', port), authkey=authkey)
    manager.start()
    print(f'Server started at port {port}')

    return manager


def make_client_manager(ip, port, authkey):
    """Create a manager for a client"""
    QueueManager.register('get_queue')
    QueueManager.register('get_maximum_depth')
    QueueManager.register('get_visited_dict')
    QueueManager.register('get_unique_constructions')
    QueueManager.register('get_point_minimal')
    manager = QueueManager(address=(ip, port), authkey=authkey)
    manager.connect()

    print(f'Client connected to {ip}:{port}')
    return manager


def run_client():
    manager = make_client_manager('192.168.254.19', 12349, b'1234')
    queue = manager.get_queue()
    point_minimal = manager.get_point_minimal()
    visited_dict = manager.get_visited_dict()
    unique_constructions = manager.get_unique_constructions()
    maximum_depth = manager.get_maximum_depth()._getvalue()
    construct_bfs_parallel_processes(queue, visited_dict, unique_constructions, point_minimal, maximum_depth)



if __name__ == '__main__':
    manager = make_server_manager(12349, b'1234')
    # Reference the shared queues and dicts.
    #queue = Global.queue()
    queue = manager.get_queue()
    point_minimal = manager.get_point_minimal()
    visited_dict = manager.get_visited_dict()
    unique_constructions = manager.get_unique_constructions()
    maximum_depth = manager.get_maximum_depth()

    # Define Construction
    construction = BaseConstruction()
    queue.put((construction, tuple(construction.points)[0]))

    # Set up the loop that will wait and print progress until completed
    start_time = time.time()
    most_recent_time = time.time()
    last_print_time = time.time()
    empty = queue.empty()

    cut_off_time = 5 * 60 * 60  # 5 hr = 5 * 60 min/hr * 60 sec/min

    while most_recent_time - start_time <= cut_off_time:
        if most_recent_time - last_print_time > 2:
            print(
                f'\033[32mMinimal Construction of Points at {time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())}')
            #print('\t', point_minimal, '\033[0m')
            print(f'\tDiscovered {len(point_minimal)} constructed points\033[0m')
            print(f'\033[33mCurrent Number of Unique Constructions (up to permuting steps) at {time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime())}')
            for num_steps, num_constructions in unique_constructions.items():
                print('\tSteps:', num_steps, 'Num Unique Constructions: ', num_constructions)
            print(f'\033[34mDiscovered {len(visited_dict)} constructions (including permutations)')

            #print(f'{queue.qsize()} items still in queue.')
            print('\033[0m')

            if empty and queue.empty():
                # If the queue is empty and has been for 2 seconds, go ahead and cancel it, since I can't find a
                # cleaner way of stopping.
                break
            else:
                empty = queue.empty()

            last_print_time = time.time()
        most_recent_time = time.time()


    print('\033[32mFinal Minimal Constructions:')
    for point, length in point_minimal.items():
        print('\t\033[32m', length, point)
    point_minimal = dict(point_minimal)

    print('\033[33mFinal Number of Unique Constructions')
    for num_steps, num_constructions in unique_constructions.items():
        print('Steps:', num_steps, 'Num Unique Constructions: ', num_constructions)
    unique_constructions = dict(unique_constructions)

    print('\033[34mFinal Unique Constructions')
    visited_list = list(visited_dict.keys())
    filehandler = open('visited_constructions.pkl', 'wb')
    pickle.dump(visited_list, filehandler)
    print(f'Visited {len(visited_list)} different constructions')

    # for construction in visited_list:
    # print(construction, '\n\n')

    try:
        filehandler2 = open('queue.pkl', 'wb')
        pickle.dump(queue._getvalue(), filehandler2)
    except:
        pass


    #item = queue.get(block=False)
    item = True
    while item:
        try:
            queue.get(block=False)
        except Empty:
            break
    # queue.join()

    time.sleep(2)
    manager.shutdown()
