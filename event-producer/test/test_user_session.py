import unittest
from datetime import datetime
from unittest.mock import MagicMock

from src.models import Location
from src.user_session import UserSession


class TestUserSession(unittest.TestCase):
    def setUp(self):
        self.mock_location = MagicMock(spec=Location)
        self.session_id = "abc123"
        self.user_agent = "Mozilla/5.0"
        self.started_at = datetime(2025, 7, 18, 12, 0, 0)
        self.user_id = "user_001"
        self.session = UserSession(
            session_id=self.session_id,
            user_agent=self.user_agent,
            started_at=self.started_at,
            user_id=self.user_id,
            location=self.mock_location
        )

    def test_initialization(self):
        self.assertEqual(self.session.session_id, self.session_id)
        self.assertEqual(self.session.user_agent, self.user_agent)
        self.assertEqual(self.session.started_at, self.started_at)
        self.assertEqual(self.session.user_id, self.user_id)
        self.assertEqual(self.session.location, self.mock_location)
        self.assertEqual(self.session.last_op_timestamp, self.started_at)
        self.assertEqual(self.session.cart, {})

    def test_get_last_op_timestamp_and_increment(self):
        before = self.session.last_op_timestamp
        returned = self.session.get_last_op_timestamp_and_increment()
        after = self.session.last_op_timestamp
        self.assertEqual(returned, before)
        self.assertGreater(after, before)

    def test_end_returns_duration(self):
        duration = self.session.end()
        self.assertGreater(duration, 0)
        self.assertGreater(self.session.last_op_timestamp, self.started_at)
