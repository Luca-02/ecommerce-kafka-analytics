import random
from datetime import datetime, timedelta

from .models import Location, Product


class UserSession:
    """
    A class representing a user session.
    """
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

    def add_to_cart(self, product: Product, quantity: int):
        """
        Adds a product to the cart.

        :param product: the product to add to the cart
        :param quantity: the quantity of the product to add to the cart
        """
        if product.id in self.cart:
            self.cart[product.id]["quantity"] += quantity
        else:
            self.cart[product.id] = {"product": product, "quantity": quantity}

    def remove_from_cart(self, product: Product, quantity: int):
        """
        Removes a product from the cart.

        :param product: the product to remove from the cart
        :param quantity: the quantity of the product to remove from the cart
        """
        if product.id not in self.cart:
            return

        current = self.cart[product.id]["quantity"]
        new_qty = max(current - quantity, 0)
        if new_qty <= 0:
            del self.cart[product.id]
        else:
            self.cart[product.id]["quantity"] = new_qty

    def purchase(self):
        """
        Purchases the cart.
        """
        self.cart.clear()

    def get_last_op_timestamp_and_increment(self) -> datetime:
        """
        Returns the last operation timestamp and increments it.

        :return: the last operation timestamp
        """
        last_op_timestamp = self.last_op_timestamp
        self._increment_last_op_timestamp()
        return last_op_timestamp

    def end(self) -> int:
        """
        Ends the session and returns the duration.

        :return: the duration of the session in seconds
        """
        self._increment_last_op_timestamp()
        duration = int((self.last_op_timestamp - self.started_at).total_seconds())
        return duration

    def _increment_last_op_timestamp(self):
        """
        Increments the last operation timestamp.
        """
        self.last_op_timestamp = self.last_op_timestamp + timedelta(minutes=random.randint(1, 5))
