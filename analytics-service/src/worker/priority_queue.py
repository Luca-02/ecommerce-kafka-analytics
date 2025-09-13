import heapq
import threading
from typing import Callable, Generic, TypeVar

from itertools import count

from ..models import Event

T = TypeVar("T")


class BlockingPriorityQueue(Generic[T]):
    def __init__(self, priority_fn: Callable[[T], float]):
        """
        Generic blocking priority queue.

        :param priority_fn: A function that, given an element T, returns its priority (numeric value).
        Lower values -> higher priority
        """
        self._heap: list[tuple[float, int, T]] = []
        self._condition = threading.Condition()
        self._priority_fn = priority_fn
        # Incrementing counter to break ties
        self._counter = count()
        self.closed = False

    def enqueue(self, item: Event):
        """
        Adds an item to the priority queue and notifies any waiting threads.

        :param item: Event to add to the queue.
        """
        with self._condition:
            if self.closed:
                return

            priority = self._priority_fn(item)
            heapq.heappush(self._heap, (priority, next(self._counter), item))
            self._condition.notify()

    def dequeue(self) -> T | None:
        """
        Removes and returns an item from the priority queue.
        Blocks if the queue is empty.
        """
        with self._condition:
            while not self._heap:
                if self.closed:
                    return None
                self._condition.wait()

            # Remove the item with the highest priority
            _, _, item = heapq.heappop(self._heap)
            return item

    def size(self) -> int:
        """
        Return the number of items in the priority queue.

        :return: Number of items in the priority queue.
        """
        return len(self._heap)

    def close(self):
        with self._condition:
            self.closed = True
            self._condition.notify_all()
