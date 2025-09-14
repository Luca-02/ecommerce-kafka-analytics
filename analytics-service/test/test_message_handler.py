from datetime import datetime
from unittest import TestCase
from unittest.mock import MagicMock

from confluent_kafka import Message

import src.message_handler as message_handler
from shared.models import (
    Event,
    EventType,
    Location,
    StartSessionParameters
)
from src.message_handler import MessageHandler


def _make_mock_record(value: str) -> Message:
    msg = MagicMock(spec=Message)
    msg.value.return_value = value
    return msg


invalid_mock_record = _make_mock_record("invalid")


class TestMessageHandler(TestCase):
    def setUp(self):
        self.mock_event = Event(
            event_id="abc123",
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
        self.scheduler = MagicMock()
        self.handler = MessageHandler(scheduler=self.scheduler)

    def test_parse_message(self):
        event = message_handler._parse_message(
            _make_mock_record(self.mock_event.model_dump_json()).value()
        )
        self.assertEqual(event, self.mock_event)

    def test_message_processor_call(self):
        mock_event_handlers_map = MagicMock()
        self.handler._event_handlers_map[self.mock_event.event_type] = mock_event_handlers_map

        self.handler.message_processor_call(
            _make_mock_record(self.mock_event.model_dump_json())
        )

        mock_event_handlers_map.handle.assert_called_once()
        args, _ = mock_event_handlers_map.handle.call_args
        self.assertIsInstance(args[0], Event)

    def test_message_processor_call_unknown_event_type(self):
        mock_logger = MagicMock()
        self.handler._logger = mock_logger

        self.handler.message_processor_call(invalid_mock_record)

        mock_logger.error.assert_called_once()
