import hashlib

from .operation import Operation
from .worker import Worker
from ..logger_utils import get_logger


class Scheduler:
    """
    Scheduler for scheduling operations to be executed by worker threads.
    The scheduler uses hash partitioning to determine which worker should process an operation.
    """

    def __init__(self, workers_count: int):
        self._logger = get_logger(component='scheduler')
        self._workers = [Worker(worker_id=i) for i in range(workers_count)]
        self.workers_count = workers_count

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        """
        Initializes and starts a pool of worker threads.
        """
        self._logger.info(f"Starting {self.workers_count} worker threads.")
        for worker in self._workers:
            # Allows the main program to exit without waiting for threads
            worker.daemon = True
            worker.start()

    def stop(self):
        """
        Stops all worker threads.
        """
        self._logger.info("Stopping all worker threads...")
        for worker in self._workers:
            worker.stop()
            worker.join()
        self._logger.info("All worker threads stopped.")

    def is_all_running(self) -> bool:
        """
        Checks if all worker threads are running.

        :return: True if all worker threads are running, False otherwise.
        """
        return all(worker.is_running for worker in self._workers)

    def _get_worker(self, operation: Operation) -> Worker:
        """
        Determines the correct worker for an operation using hash partitioning with SHA-256 hash function.

        :param operation: The operation to schedule.
        :return: The worker to schedule the operation on.
        """
        worker_id_bytes = operation.partition_key.encode('utf-8')
        hash_value = int(hashlib.sha256(worker_id_bytes).hexdigest(), 16)
        worker_index = hash_value % self.workers_count
        return self._workers[worker_index]

    def schedule(self, operation: Operation):
        """
        Schedules an operation to be executed by one of the worker using hash partitioning.

        :param operation: The operation to schedule.
        """
        worker = self._get_worker(operation)
        worker.schedule(operation)
