import threading
from unittest import TestCase

import time

from src.worker.priority_queue import BlockingPriorityQueue


class TestBlockingPriorityQueue(TestCase):
    def setUp(self):
        self.queue = BlockingPriorityQueue(priority_fn=lambda x: x)

    def test_enqueue_and_dequeue_single(self):
        self.queue.enqueue(10)
        item = self.queue.dequeue()
        self.assertEqual(item, 10)

    def test_priority_order(self):
        items = [5, 1, 3, 4, 2, 8, 10, 3, 6, 49, 1]
        sorted_items = items.copy()
        sorted_items.sort()

        for item in items:
            self.queue.enqueue(item)

        results = [self.queue.dequeue() for _ in range(len(items))]

        self.assertEqual(results, sorted_items)

    def test_blocking_behavior(self):
        results: list[int] = []
        delay = [0]
        sleep = 0.2

        def consumer():
            now = time.time()
            results.append(self.queue.dequeue())
            delay[0] = time.time() - now

        t = threading.Thread(target=consumer)
        t.start()

        time.sleep(sleep)
        self.assertEqual(results, [])

        self.queue.enqueue(42)
        t.join(timeout=10)

        self.assertEqual(results, [42])
        self.assertGreaterEqual(delay[0], sleep)

    def test_multiple_producers_consumers(self):
        queue = BlockingPriorityQueue(priority_fn=lambda x: x)
        results: list[int] = []

        def producer(values):
            for v in values:
                queue.enqueue(v)

        def consumer(count):
            for _ in range(count):
                item = queue.dequeue()
                results.append(item)

        producers = [
            threading.Thread(target=producer, args=([5, 1, 3],)),
            threading.Thread(target=producer, args=([2, 4],)),
        ]
        consumers = [
            threading.Thread(target=consumer, args=(3,)),
            threading.Thread(target=consumer, args=(2,)),
        ]

        for t in producers + consumers:
            t.start()
        for t in producers + consumers:
            t.join()

        self.assertEqual(sorted(results), [1, 2, 3, 4, 5])

    def test_custom_priority_function(self):
        class Task:
            def __init__(self, priority, name):
                self.priority = priority
                self.name = name

        def priority_fn(t: Task):
            return t.priority

        queue = BlockingPriorityQueue(priority_fn=priority_fn)

        queue.enqueue(Task(1, "high"))
        queue.enqueue(Task(1, "high"))
        queue.enqueue(Task(2, "medium"))
        queue.enqueue(Task(2, "medium"))
        queue.enqueue(Task(3, "low"))
        queue.enqueue(Task(3, "low"))

        results = []
        while queue.size() > 0:
            results.append(queue.dequeue().name)

        self.assertEqual(results, ["high", "high", "medium", "medium", "low", "low"])
