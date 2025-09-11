from unittest.mock import MagicMock

import src.message_handler as message_handler

from kafka.consumer.fetcher import ConsumerRecord
from datetime import datetime
from unittest import TestCase

from src.message_handler import MessageHandler
from src.models import (
    Event,
    EventType,
    Location,
    StartSessionParameters
)


def _make_mock_record(value: str):
    return ConsumerRecord(
        topic="test-topic",
        partition=0,
        leader_epoch=0,
        offset=0,
        timestamp=0,
        timestamp_type=0,
        key=None,
        value=value,
        headers=[],
        checksum=None,
        serialized_key_size=-1,
        serialized_value_size=len(value),
        serialized_header_size=-1,
    )


invalid_mock_record = _make_mock_record("invalid")


class TestMessageHandler(TestCase):
    def setUp(self):
        self.mock_event = Event(
            event_type=EventType.SESSION_STARTED,
            session_id="abc123",
            timestamp=datetime.now(),
            user_id="user_42",
            location=Location(
                country="Italy",
                state="Lazio",
                city="Rome",
                latitude=41.9,
                longitude=12.5
            ),
            parameters=StartSessionParameters(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            )
        )
        self.handler = MessageHandler()

    def test_parse_message(self):
        event = message_handler._parse_message(
            _make_mock_record(self.mock_event.model_dump_json())
        )
        self.assertEqual(event, self.mock_event)

    def test_handle_event(self):
        mock_handler = MagicMock()
        self.handler.event_handlers_map[self.mock_event.event_type] = mock_handler

        self.handler.handle(
            _make_mock_record(self.mock_event.model_dump_json())
        )

        mock_handler.handle.assert_called_once()
        args, _ = mock_handler.handle.call_args
        self.assertIsInstance(args[0], Event)
