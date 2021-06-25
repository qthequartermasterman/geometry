from .MinimalConstructionsCore import (construction_job_queue, point_minimal_construction_length, maximum_depth,
                                       generated_constructions, Queue, base_construction, results_dir,
                                       count_unique_constructions, print_report)
from multiprocessing.managers import SyncManager
import multiprocessing.managers as managers
from queue import Empty
import time
import pickle


# Helper functions for our multiprocessing servers. These are not lambdas, since those are not pickle-able.
def return_queue(): return construction_job_queue


def return_point_minimal(): return point_minimal_construction_length


def return_maximum_depth(): return maximum_depth


def return_visited_dict(): return generated_constructions


class QueueManager(SyncManager):
    """Custom multiprocessing manager subclassing SyncManager. Only difference is later we will register various
    custom methods for consistency across clients. """
    pass


def make_server_manager(port, authkey):
    """Create a manager for the server, listening on the given port."""
    # Register the getter functions for queue, max depth, visited, etc...
    # We need to register these functions so that our client managers can use the shared state data.
    QueueManager.register('get_queue', return_queue)
    QueueManager.register('get_maximum_depth', return_maximum_depth)
    QueueManager.register('get_visited_dict', return_visited_dict, managers.DictProxy)
    QueueManager.register('get_point_minimal', return_point_minimal, managers.DictProxy)

    # Create the server manager and start
    # Bind to all addresses, so address is empty string
    server_manager = QueueManager(address=('', port), authkey=authkey)
    server_manager.start()
    print(f'Server started at port {port}')
    return server_manager


def run_bfs_in_parallel():
    manager = make_server_manager(12349, b'1234')
    # Reference the shared queues and dicts.
    check_construction_job_queue = manager.get_queue()
    dict_point_minimal_construction_length = manager.get_point_minimal()
    generated_constructions_dict = manager.get_visited_dict()
    maximum_search_depth = manager.get_maximum_depth()

    # Define Construction
    base_construction = base_construction()
    check_construction_job_queue.put((base_construction, tuple(base_construction.points)[0]))

    # run_client()

    # Set up the loop that will wait and print progress until completed
    start_time = time.time()
    most_recent_time = time.time()
    last_print_time = time.time()
    empty = check_construction_job_queue.empty()

    cut_off_time = 5 * 60 * 60  # 5 hr = 5 * 60 min/hr * 60 sec/min

    while most_recent_time - start_time <= cut_off_time:
        if most_recent_time - last_print_time > 2:
            unique_constructions = count_unique_constructions(generated_constructions_dict.keys())
            print_report(dict_point_minimal_construction_length, unique_constructions,
                         generated_constructions_dict.keys())
            if empty and check_construction_job_queue.empty():
                # If the queue is empty and has been for 2 seconds, go ahead and cancel it, since I can't find a
                # cleaner way of stopping.
                break
            else:
                empty = check_construction_job_queue.empty()

            last_print_time = time.time()
        most_recent_time = time.time()

    # Perform our final report
    # Minimal Construction Length for each point
    dict_point_minimal_construction_length = dict(dict_point_minimal_construction_length)
    # Number of unique constructions of each length (categorized)
    unique_constructions = count_unique_constructions(generated_constructions_dict.keys())
    # Total number of unique constructions generated (not necessarily categorized by length)
    generated_construction_list = list(generated_constructions_dict.keys())

    print_report(dict_point_minimal_construction_length, unique_constructions, generated_construction_list)

    # Save the generated list to disc.
    with open(results_dir + 'visited_constructions.pkl', 'wb') as visited_constructions_file:
        pickle.dump(generated_construction_list, visited_constructions_file)

    # Save the job queue (for future analysis)
    try:
        with open(results_dir + 'queue.pkl', 'wb') as construction_queue_file:
            pickle.dump(check_construction_job_queue._getvalue(), construction_queue_file)
    except:
        pass

    # Empty the job queue
    item = True
    while item:
        try:
            item = check_construction_job_queue.get(block=False)
        except Empty:
            break

    time.sleep(2)
    manager.shutdown()


if __name__ == '__main__':
    run_bfs_in_parallel()
