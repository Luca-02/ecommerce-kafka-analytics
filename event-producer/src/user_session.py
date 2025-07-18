import random
from datetime import datetime, timedelta

from .models import Location


class UserSession:
    def __init__(
        self,
        session_id: str,
        user_agent: str,
        started_at: datetime,
        user_id: str,
        location: Location
    ):
        self.session_id = session_id
        self.user_agent = user_agent
        self.started_at = started_at
        self.user_id = user_id
        self.location = location
        self.last_op_timestamp = started_at
        self.cart: dict[str, dict] = {}

    def end(self) -> int:
        self.__increment_last_op_timestamp()
        duration = int((self.last_op_timestamp - self.started_at).total_seconds())
        return duration

    def get_last_op_timestamp_and_increment(self) -> datetime:
        last_op_timestamp = self.last_op_timestamp
        self.__increment_last_op_timestamp()
        return last_op_timestamp

    def __increment_last_op_timestamp(self):
        self.last_op_timestamp = self.last_op_timestamp + timedelta(minutes=random.randint(1, 5))
