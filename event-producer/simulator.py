import random
import uuid
from datetime import datetime

from producer import Producer
from repository import Repository
from models import (
    Event,
    EventType,
    Product,
    UserSession
)

class Simulator:
    def __init__(
        self,
        repository: Repository = Repository(),
        producer: Producer = Producer()
    ):
        self.repository = repository
        self.producer = producer

    def simulate_user_session(self):
        user, location = self.repository.get_random_user()
        session = UserSession(
            session_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            user_id=user.id,
            location=location
        )

        # Start session
        self._produce_event(session, EventType.SESSION_STARTED)

        # View categories
        for category in self.repository.get_categories_sample():
            self._produce_event(session, EventType.CATEGORY_VIEWED, EventMetadata(category=category))

            # View products in category
            for product in self.repository.get_products_sample_by_category(category):
                self._produce_event(session, EventType.PRODUCT_VIEWED, EventMetadata(product=product))

                # Add to cart with 50% probability with a random quantity from 1 to 5
                if random.random() < 0.5:
                    quantity = random.randint(1, 5)
                    self._add_to_cart(session, product, quantity)

        # Remove random quantity from cart with 25% probability
        for item in session.cart.values():
            if random.random() < 0.25:
                to_remove = random.randint(1, item["quantity"])
                self._remove_from_cart(session, item["product"], to_remove)

        # Purchase with 75% probability
        if session.cart and random.random() < 0.75:
            self._purchase(session)

        # End session
        self._produce_event(session, EventType.SESSION_ENDED)

    def _add_to_cart(self, session: UserSession, product: Product, quantity: int):
        if product.id in session.cart:
            session.cart[product.id]["quantity"] += quantity
        else:
            session.cart[product.id] = {"product": product, "quantity": quantity}

        self._produce_event(
            session,
            EventType.PRODUCT_ADDED_TO_CART,
            EventMetadata(product=product, quantity=quantity)
        )

    def _remove_from_cart(self, session: UserSession, product: Product, quantity: int):
        if product.id not in session.cart:
            return

        current = session.cart[product.id]["quantity"]
        new_qty = max(current - quantity, 0)
        if new_qty <= 0:
            del session.cart[product.id]
        else:
            session.cart[product.id]["quantity"] = new_qty

        self._produce_event(
            session,
            EventType.PRODUCT_REMOVED_FROM_CART,
            EventMetadata(product=product, quantity=quantity)
        )

    def _purchase(self, session: UserSession):
        items = []
        total = 0
        for item in session.cart.values():
            p = item["product"]
            q = item["quantity"]
            subtotal = round(p.price * q, 2)
            items.append({
                "product": p,
                "quantity": q,
                "subtotal": subtotal
            })
            total += subtotal

        session.cart.clear()

        self._produce_event(
            session,
            EventType.PURCHASE,
            EventMetadata(items=items, total_amount=round(total, 2))
        )

    def _produce_event(self, session: UserSession, event_type: EventType, metadata: EventMetadata = None):
        event = Event(
            event_type=event_type,
            session_id=session.session_id,
            timestamp=session.get_timestamp_and_increment(),
            user_id=session.user_id,
            location=session.location,
            metadata=metadata
        )
        self.producer.produce(event)