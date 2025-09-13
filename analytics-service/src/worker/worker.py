import threading

from .operation import Operation
from .priority_queue import BlockingPriorityQueue
from ..logger_utils import get_logger


def _priority_fn(op: Operation):
    """
    Priority function for the priority queue.
    """
    return op.priority_value


class Worker(threading.Thread):
    """
    Worker thread that processes operations from a priority queue.
    """

    def __init__(self, worker_id: str):
        super().__init__()
        self.worker_id = worker_id
        self._logger = get_logger(component=f'worker-{self.worker_id}')
        self._op_queue = BlockingPriorityQueue(priority_fn=_priority_fn)
        self.is_running = True

    def _process_operation(self, op: Operation):
        if op:
            self._logger.info(f"Processing operation: {op.partition_key}")
            op.call()

    def run(self):
        """
        The main worker loop. Continuously dequeues and processes operations from the priority queue.
        """
        self._logger.info("Worker started.")
        try:
            while self.is_running:
                try:
                    op = self._op_queue.dequeue()
                    self._process_operation(op)
                except Exception as e:
                    self._logger.error(f"Worker error while processing operations: {e}")
        except KeyboardInterrupt:
            self._logger.info(f"Consumer stopped by user.")
        finally:
            self._logger.info("Worker finished.")

    def schedule(self, operation):
        self._op_queue.enqueue(operation)

    def stop(self):
        """
        Stop the worker thread.
        """
        self._logger.info("Stopping worker...")
        self._op_queue.close()
        self.is_running = False
