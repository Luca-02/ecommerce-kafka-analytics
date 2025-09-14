from abc import ABC, abstractmethod

from shared.logger import get_logger


class EventHandler(ABC):
    """
    Abstract base class for event handlers.
    """

    def __init__(self):
        self.logger = get_logger(component='event-handler')

    @abstractmethod
    def handle(self, event):
        """
        Handle the event.

        :param event: The event to handle.
        """
        pass


class SessionStartedHandler(EventHandler):
    def handle(self, event):
        self.logger.info(f"Session started: {event}")


class SessionEndedHandler(EventHandler):
    def handle(self, event):
        self.logger.info(f"Session ended: {event}")


class CategoryViewedHandler(EventHandler):
    def handle(self, event):
        self.logger.info(f"Category viewed: {event}")


class ProductViewedHandler(EventHandler):
    def handle(self, event):
        self.logger.info(f"Product viewed: {event}")


class ProductAddedToCartHandler(EventHandler):
    def handle(self, event):
        self.logger.info(f"Product added to cart: {event}")


class ProductRemovedFromCartHandler(EventHandler):
    def handle(self, event):
        self.logger.info(f"Product removed from cart: {event}")


class PurchasedHandler(EventHandler):
    def handle(self, event):
        self.logger.info(f"Purchased: {event}")
