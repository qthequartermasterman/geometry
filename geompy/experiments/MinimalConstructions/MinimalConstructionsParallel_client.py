from geompy import Point, Construction
from .MinimalConstructionsCore import BaseConstruction, Queue, generate_constructions_breadth_first_search
from .MinimalConstructionsParallel_server import QueueManager

from multiprocessing import Process, cpu_count


def construct_bfs_parallel_processes(job_queue: Queue, initialized_construction_dict: {Construction: int},
                                     point_minimal_construction_dict: {Point, int}, max_depth: int) -> [Process]:
    # Initialize processes. Each process will do construct_bfs_parallel.
    num_processes = cpu_count()  # We want to maximize the process count of each client in our cluster. Use every CPU!
    processes = [Process(target=generate_constructions_breadth_first_search,
                         args=(job_queue, initialized_construction_dict,
                               point_minimal_construction_dict, max_depth,))
                 for _ in range(num_processes)]
    # Start each process
    for process in processes:
        process.start()
    return processes


def make_client_manager(ip, port, authkey):
    """Create a manager for a client"""
    # Register the getter functions for queue, max depth, visited, etc...
    # We need to register these functions so that our client managers can use the shared state data.
    QueueManager.register('get_queue')
    QueueManager.register('get_maximum_depth')
    QueueManager.register('get_visited_dict')
    # QueueManager.register('get_unique_constructions')
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


if __name__ == '__main__':
    run_client()
