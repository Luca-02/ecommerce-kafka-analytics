import random
import time
import uuid
from datetime import datetime, timedelta

from loguru import logger

from config import (
    ADD_TO_CART_PROBABILITY,
    DELIVERY_DAYS_RANGE,
    DISCOUNT_PROBABILITY,
    MAX_CART_QUANTITY,
    MAX_EVENT_INTERVAL_SECONDS,
    MAX_SESSION_INTERVAL_SECONDS,
    MAX_SHIPPING_COST,
    MIN_CART_QUANTITY,
    MIN_EVENT_INTERVAL_SECONDS,
    MIN_SESSION_INTERVAL_SECONDS,
    MIN_SHIPPING_COST,
    PURCHASE_PROBABILITY,
    REMOVE_FROM_CART_PROBABILITY
)
from .models import (
    CartMetadata,
    CategoryMetadata,
    EndSessionMetadata,
    Event,
    EventMetadata,
    EventType,
    Product,
    ProductMetadata,
    PurchaseItem,
    PurchaseMetadata,
    StartSessionMetadata
)
from .producer import Producer
from .repository import Repository
from .user_session import UserSession


def sleep(min_seconds: float, max_seconds: float):
    sleep_time = random.uniform(min_seconds, max_seconds)
    time.sleep(sleep_time)


class Simulator:
    def __init__(
        self,
        repository: Repository,
        producer: Producer
    ):
        self.repository = repository
        self.producer = producer

    def run(self):
        self.producer.connect_to_kafka()
        logger.info("Starting event simulator...")
        try:
            while True:
                self.simulate_user_session()
                sleep(MIN_SESSION_INTERVAL_SECONDS, MAX_SESSION_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logger.info("Simulation stopped by user.")
        finally:
            logger.info("Finishing event simulator...")
            self.producer.close()

    def simulate_user_session(self):
        user, location = self.repository.get_random_user()
        user_agent = self.repository.get_random_user_agent()
        session = UserSession(
            session_id=str(uuid.uuid4()),
            user_agent=user_agent,
            started_at=datetime.now(),
            user_id=user.id,
            location=location
        )

        logger.info(f"[Simulator] Simulating user session {session.session_id} for user {user.id}...")

        # Start session
        self._produce_event(
            EventType.SESSION_STARTED,
            session,
            StartSessionMetadata(user_agent=session.user_agent)
        )

        # View categories
        for category in self.repository.get_categories_sample():
            self._produce_event(
                EventType.CATEGORY_VIEWED,
                session,
                CategoryMetadata(category=category)
            )

            # View products in category
            for product in self.repository.get_products_sample_by_category(category):
                self._produce_event(
                    EventType.PRODUCT_VIEWED,
                    session,
                    ProductMetadata(product=product)
                )

                # Add to cart
                if random.random() < ADD_TO_CART_PROBABILITY:
                    quantity = random.randint(MIN_CART_QUANTITY, MAX_CART_QUANTITY)
                    self._add_to_cart(session, product, quantity)

        # Remove quantity from cart
        for item in list(session.cart.values()):
            if random.random() < REMOVE_FROM_CART_PROBABILITY:
                to_remove = random.randint(1, item["quantity"])
                self._remove_from_cart(session, item["product"], to_remove)

        # Purchase with 75% probability
        if session.cart and random.random() < PURCHASE_PROBABILITY:
            self._purchase(session)

        # End session
        self._produce_event(
            EventType.SESSION_ENDED,
            session,
            EndSessionMetadata(seconds_duration=session.end())
        )

    def _add_to_cart(self, session: UserSession, product: Product, quantity: int):
        if product.id in session.cart:
            session.cart[product.id]["quantity"] += quantity
        else:
            session.cart[product.id] = {"product": product, "quantity": quantity}

        self._produce_event(
            EventType.PRODUCT_ADDED_TO_CART,
            session,
            CartMetadata(product=product, quantity=quantity)
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
            EventType.PRODUCT_REMOVED_FROM_CART,
            session,
            CartMetadata(product=product, quantity=quantity)
        )

    def _purchase(self, session: UserSession):
        items = []
        total_products_amount = 0
        for item in session.cart.values():
            p = item["product"]
            q = item["quantity"]
            subtotal = round(p.price * q, 2)
            items.append(PurchaseItem(
                product=p,
                quantity=q,
                subtotal=subtotal
            ))
            total_products_amount += subtotal
        total_products_amount = round(total_products_amount, 2)
        session.cart.clear()

        # Apply discount
        if random.random() < DISCOUNT_PROBABILITY:
            discount_amount = round(random.uniform(0, total_products_amount / 2), 2)
        else:
            discount_amount = 0
        shipping_cost = round(random.uniform(MIN_SHIPPING_COST, MAX_SHIPPING_COST), 2)
        payment_method = self.repository.get_random_payment_method()
        estimated_delivery_date = session.last_op_timestamp + timedelta(
            days=random.randint(*DELIVERY_DAYS_RANGE)
        )

        self._produce_event(
            EventType.PURCHASE,
            session,
            PurchaseMetadata(
                items=items,
                total_amount=total_products_amount - discount_amount + shipping_cost,
                discount_amount=discount_amount,
                shipping_address=session.location,
                shipping_cost=shipping_cost,
                payment_method=payment_method,
                estimated_delivery_date=estimated_delivery_date
            )
        )

    def _produce_event(self, event_type: EventType, session: UserSession, metadata: EventMetadata = None):
        event = Event(
            event_type=event_type,
            session_id=session.session_id,
            timestamp=session.get_last_op_timestamp_and_increment(),
            user_id=session.user_id,
            location=session.location,
            metadata=metadata
        )
        sleep(MIN_EVENT_INTERVAL_SECONDS, MAX_EVENT_INTERVAL_SECONDS)
        self.producer.produce(event)
