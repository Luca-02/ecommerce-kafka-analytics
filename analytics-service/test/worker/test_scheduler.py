from multiprocessing import Event
from unittest import TestCase
from unittest.mock import MagicMock

from src.worker.scheduler import Operation
from src.worker.scheduler import Scheduler


class TestScheduler(TestCase):
    def setUp(self):
        self.scheduler = Scheduler(workers_count=2)
        self.scheduler.start()

    def tearDown(self):
        self.scheduler.stop()

    def test_scheduler_context_manager(self):
        with Scheduler(workers_count=2) as scheduler:
            self.assertTrue(scheduler.is_all_running())
        self.assertFalse(scheduler.is_all_running())

    def test_worker_assignment(self):
        op1 = Operation(partition_key="op1", priority_value=1.0, call=MagicMock())
        op2 = Operation(partition_key="op2", priority_value=2.0, call=MagicMock())

        worker1 = self.scheduler._get_worker(op1)
        worker2 = self.scheduler._get_worker(op2)

        self.assertIn(worker1, self.scheduler._workers)
        self.assertIn(worker2, self.scheduler._workers)

    def test_operation_processing(self):
        operations = []
        expected_operations = list(range(10))
        operation_count = 10
        done_event = Event()

        def make_task(op, is_last=False):
            def task():
                operations.append(op)
                if is_last:
                    done_event.set()

            return task

        for i in range(operation_count):
            self.scheduler.schedule(Operation(
                partition_key=i,
                priority_value=1.0,
                call=make_task(i, is_last=i == operation_count - 1)
            ))

        done_event.wait(timeout=10)

        operations.sort()
        self.assertEqual(operations, expected_operations)
