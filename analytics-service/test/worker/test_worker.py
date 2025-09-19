from threading import Event
from unittest import TestCase

from src.worker.worker import Worker
from src.worker.scheduler import Operation


class TestWorker(TestCase):
    def test_worker_executes_operations_in_priority_order(self):
        executed = []
        done_event = Event()

        def make_task(name, is_last=False):
            def task():
                executed.append(name)
                if is_last:
                    done_event.set()
            return task

        worker = Worker(worker_id=1)
        worker.start()

        worker.schedule(Operation(partition_key=1, priority_value=3, call=make_task("low")))
        worker.schedule(Operation(partition_key=2, priority_value=1, call=make_task("high")))
        worker.schedule(Operation(partition_key=3, priority_value=2, call=make_task("medium", is_last=True)))

        done_event.wait(timeout=10)

        worker.stop()
        worker.join()

        self.assertEqual(executed, ["high", "medium", "low"])

    def test_worker_can_stop_with_empty_queue(self):
        worker = Worker(worker_id=2)
        worker.start()
        worker.stop()
        worker.join()

        self.assertTrue(True)
