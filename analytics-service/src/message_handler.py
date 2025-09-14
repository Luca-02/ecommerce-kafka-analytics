import json
from json import JSONDecodeError

import time
from confluent_kafka import Message, TIMESTAMP_NOT_AVAILABLE

from shared.logger import get_logger
from shared.models import Event, EventType
from .event_processor import (CategoryViewedHandler, EventHandler, ProductAddedToCartHandler,
                              ProductRemovedFromCartHandler, ProductViewedHandler, PurchasedHandler,
                              SessionEndedHandler,
                              SessionStartedHandler)
from .worker.operation import Operation
from .worker.scheduler import Scheduler


def _parse_message(payload: bytes) -> Event:
    """
    Kafka message parser method.

    :param payload: Message payload to parse.
    :return: Parsed event object.
    """
    event_json = json.loads(payload)
    return Event(**event_json)


class MessageHandler:
    """
    Message handler class, that handles the consumed Kafka messages.
    """

    def __init__(self, scheduler: Scheduler):
        self._logger = get_logger(component='message-handler')
        self._scheduler = scheduler
        self._event_handlers_map: dict[EventType, EventHandler] = {
            EventType.SESSION_STARTED: SessionStartedHandler(),
            EventType.SESSION_ENDED: SessionEndedHandler(),
            EventType.CATEGORY_VIEWED: CategoryViewedHandler(),
            EventType.PRODUCT_VIEWED: ProductViewedHandler(),
            EventType.PRODUCT_ADDED_TO_CART: ProductAddedToCartHandler(),
            EventType.PRODUCT_REMOVED_FROM_CART: ProductRemovedFromCartHandler(),
            EventType.PURCHASE: PurchasedHandler()
        }

    def _process_event(self, event: Event):
        """
        Process the event using the appropriate event handler.

        :param event: Event object.
        """
        self._logger.info(f"Processing event {event.event_type} with id: {event.event_id}")
        event_handler = self._event_handlers_map.get(event.event_type)
        if event_handler:
            event_handler.handle(event)
        else:
            self._logger.warning(f"Unknown event type: {event.event_type}")

    def message_processor_call(self, msg: Message):
        try:
            event = _parse_message(msg.value())
            self._process_event(event)
        except JSONDecodeError as e:
            self._logger.error(f"JSON decoding error for message: {e}")
        except Exception as e:
            self._logger.error(f"Error while processing message: {e}")

    def handle(self, msg: Message):
        """
        Handles the consumed Kafka message.

        :param msg: Consumed Kafka message.
        """
        partition_key = msg.key()

        timestamp_type, timestamp_value = msg.timestamp()
        if timestamp_type == TIMESTAMP_NOT_AVAILABLE:
            # If timestamp is not available, use current system time as fallback
            priority_value = int(time.time() * 1000)
            self._logger.warning(
                f"Timestamp not available for message. Using current system time as fallback. "
            )
        else:
            priority_value = timestamp_value

        self._scheduler.schedule(Operation(
            partition_key=partition_key,
            priority_value=priority_value,
            call=lambda: self.message_processor_call(msg),
        ))
