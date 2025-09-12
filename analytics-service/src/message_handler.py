import json
from json import JSONDecodeError

from confluent_kafka import Message

from .event_handler import (CategoryViewedHandler, EventHandler, ProductAddedToCartHandler,
                           ProductRemovedFromCartHandler, ProductViewedHandler, PurchasedHandler, SessionEndedHandler,
                           SessionStartedHandler)
from .logger_utils import get_logger
from .models import Event, EventType


def _parse_message(message: Message) -> Event:
    """
    Kafka message parser method.

    :param message: Consumed Kafka message.
    :return: Parsed event object.
    """
    event_json = json.loads(message.value())
    return Event(**event_json)


class MessageHandler:
    """
    Message handler class, that handles the consumed Kafka messages.
    """

    def __init__(self):
        self.logger = get_logger(component='message-handler')
        self.event_handlers_map: dict[EventType, EventHandler] = {
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
        self.logger.info(f"Processing: {event}")
        event_handler = self.event_handlers_map.get(event.event_type)
        if event_handler:
            event_handler.handle(event)
        else:
            self.logger.warning(f"Unknown event type: {event.event_type}")

    def handle(self, message: Message):
        """
        Handles the consumed Kafka message.

        :param message: Consumed Kafka message.
        """
        try:
            event = _parse_message(message)
            self._process_event(event)
        except JSONDecodeError as e:
            self.logger.error(f"JSON decoding error for message: {e}")
        except Exception as e:
            self.logger.error(f"Error while processing message: {e}")
