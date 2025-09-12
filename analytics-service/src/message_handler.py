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

# TODO i messaggi arrivano in ordine, però vorrei aggiungere parallelismo tra gli eventi delle sessioni, ad esempio
#  potrei suddividere gli eventi delle sessioni (che possono essere mischiati tra sessioni) in più thread worker tramite
#  hash partitioning, così che gli eventi ordinati di una stessa sessione vadano nello stesso worker. Un po come funziona già kafka,
#  che tramite la key che uso nel messaggio spartisce i messaggi kafka tra i nodi consumer che fanno parte dello stesso group_id, in
#  modo che gli eventi di una stessa sessione vadano nello stesso nodo consumer.

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
        self.logger.info(f"Processing event {event.event_type} with id: {event.event_id}")
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
