from typing import Callable


class Operation:
    def __init__(self, partition_key: str, priority_value: float, call: Callable):
        self.partition_key = str(partition_key)
        self.priority_value = priority_value
        self.call = call
