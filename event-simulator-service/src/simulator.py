import random
import time
import uuid
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel

from shared.logger import get_logger
from shared.models import (
    CartParameters,
    CategoryParameters,
    EndSessionParameters,
    Event,
    EventParameters,
    EventType,
    Product, ProductParameters,
    PurchaseItem,
    PurchaseParameters,
    StartSessionParameters
)
from .producer import Producer
from .repository import Repository
from .user_session import UserSession


def sleep(min_seconds: float, max_seconds: float):
    """
    Pauses execution for a random duration within a specified range.

    :param min_seconds: Minimum duration in seconds.
    :param max_seconds: Maximum duration in seconds.
    """
    if max_seconds >= min_seconds > 0:
        sleep_time = random.uniform(min_seconds, max_seconds)
        time.sleep(sleep_time)


class SimulatorConfig(BaseModel):
    add_to_cart_probability: float
    remove_from_cart_probability: float
    discount_probability: float
    purchase_probability: float
    cart_quantity_range: tuple[int, int]
    shipping_cost_range: tuple[float, float]
    delivery_days_range: tuple[int, int]
    session_interval_seconds_range: tuple[int, int]
    event_interval_seconds_range: tuple[int, int]


class Simulator:
    """
    Simulates user behavior on an e-commerce platform, generating events
    and sending them to Kafka.
    """

    def __init__(
        self,
        process_id: int,
        event_topic: str,
        repository: Repository,
        producer: Producer,
        config: SimulatorConfig
    ):
        self._logger = get_logger(component=f'simulator-{process_id}')
        self._event_topic = event_topic
        self._repository = repository
        self._producer = producer
        self._config = config

    def _start_session_event(self, session: UserSession):
        self._produce_event(
            EventType.SESSION_STARTED,
            session,
            StartSessionParameters(user_agent=session.user_agent)
        )

    def _simulate_browse(self, session: UserSession):
        for category in self._repository.get_categories_sample():
            self._produce_event(
                EventType.CATEGORY_VIEWED,
                session,
                CategoryParameters(category=category)
            )

            for product in self._repository.get_products_sample_by_category(category):
                self._produce_event(
                    EventType.PRODUCT_VIEWED,
                    session,
                    ProductParameters(product=product)
                )
                self._handle_add_to_cart(session, product)

    def _handle_add_to_cart(self, session: UserSession, product: Product):
        if random.random() < self._config.add_to_cart_probability:
            quantity = random.randint(*self._config.cart_quantity_range)
            session.add_to_cart(product, quantity)
            self._produce_event(
                EventType.PRODUCT_ADDED_TO_CART,
                session,
                CartParameters(product=product, quantity=quantity)
            )

    def _simulate_cart_modifications(self, session: UserSession):
        for item in list(session.cart.values()):
            if random.random() < self._config.remove_from_cart_probability:
                product = item["product"]
                to_remove = random.randint(1, item["quantity"])
                session.remove_from_cart(item["product"], to_remove)
                self._produce_event(
                    EventType.PRODUCT_REMOVED_FROM_CART,
                    session,
                    CartParameters(product=product, quantity=to_remove)
                )

    def _simulate_purchase(self, session: UserSession):
        if session.cart and random.random() < self._config.purchase_probability:
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
            session.purchase()

            # Apply discount
            discount_amount = self._calculate_discount(total_products_amount)
            shipping_cost = round(random.uniform(*self._config.shipping_cost_range), 2)
            payment_method = self._repository.get_random_payment_method()
            estimated_delivery_date = session.last_op_timestamp + timedelta(
                days=random.randint(*self._config.delivery_days_range)
            )

            self._produce_event(
                EventType.PURCHASE,
                session,
                PurchaseParameters(
                    items=items,
                    total_amount=total_products_amount,
                    discount_amount=discount_amount,
                    shipping_address=session.location,
                    shipping_cost=shipping_cost,
                    payment_method=payment_method,
                    estimated_delivery_date=estimated_delivery_date
                )
            )

    def _calculate_discount(self, total_amount: float) -> float:
        discount_amount = 0.0
        if random.random() < self._config.discount_probability:
            discount_amount = round(random.uniform(0, total_amount / 2), 2)
        return discount_amount

    def _end_session_event(self, session: UserSession):
        self._produce_event(
            EventType.SESSION_ENDED,
            session,
            EndSessionParameters(seconds_duration=session.end())
        )

    def run(self):
        """
        Starts the event simulation. Connects to Kafka and continuously
        simulates user sessions.
        """
        self._logger.info(f"Simulator started...")
        try:
            while True:
                sleep(*self._config.session_interval_seconds_range)
                self.simulate_user_session()
        except KeyboardInterrupt:
            self._logger.info(f"Simulator stopped by user.")

    def simulate_user_session(self):
        """
        Simulates a single user session, including viewing categories/products,
        adding/removing from cart, and making a purchase.
        """
        user, location = self._repository.get_random_user()
        user_agent = self._repository.get_random_user_agent()
        session = UserSession(
            session_id=str(uuid.uuid4()),
            user_agent=user_agent,
            started_at=datetime.now(timezone.utc),
            user_id=user.id,
            location=location
        )

        self._logger.info(f"Simulating user session {session.session_id} for user {user.id}...")
        self._start_session_event(session)
        self._simulate_browse(session)
        self._simulate_cart_modifications(session)
        self._simulate_purchase(session)
        self._end_session_event(session)

    def _produce_event(
        self,
        event_type: EventType,
        session: UserSession,
        metadata: EventParameters = None
    ):
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            session_id=session.session_id,
            timestamp=session.get_last_op_timestamp_and_increment(),
            user_id=session.user_id,
            location=session.location,
            parameters=metadata
        )
        self._producer.produce(self._event_topic, event)
        sleep(*self._config.event_interval_seconds_range)
