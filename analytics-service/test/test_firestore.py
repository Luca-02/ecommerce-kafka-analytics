from datetime import datetime, timedelta, timezone

import config
from shared.models import CartParameters, Category, CategoryParameters, Event, EventType, Location, PaymentMethod, \
    Product, \
    ProductParameters, \
    PurchaseItem, PurchaseParameters, StartSessionParameters
from src.event_processor import CategoryViewedProcessor, ProductAddedToCartProcessor, ProductRemovedFromCartProcessor, \
    ProductViewedProcessor, \
    PurchaseProcessor, SessionStartedProcessor
from src.repository import FirebaseRepository

payment_method1 = PaymentMethod(
    id="payment-1",
    name="Payment Method 1"
)
payment_method2 = PaymentMethod(
    id="payment-2",
    name="Payment Method 2"
)
category1 = Category(
    id="category-1",
    name="Category 1"
)
category2 = Category(
    id="category-2",
    name="Category 2"
)
product1 = Product(
    id="id1",
    name="name1",
    category=category1,
    price=50,
    currency="USD"
)
product2 = Product(
    id="id2",
    name="name2",
    category=category2,
    price=100,
    currency="USD"
)


def test_session_started(repo):
    processor = SessionStartedProcessor(repo)
    events = [
        Event(
            event_id="test1",
            event_type=EventType.SESSION_STARTED,
            session_id="session-1",
            timestamp=datetime.now(timezone.utc),
            user_id="user-1",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=StartSessionParameters(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            )
        ),
        Event(
            event_id="test2",
            event_type=EventType.SESSION_STARTED,
            session_id="session-2",
            timestamp=datetime.now(timezone.utc),
            user_id="user-2",
            location=Location(
                country="US",
                state="State",
                city="City",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=StartSessionParameters(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            )
        ),
        Event(
            event_id="test3",
            event_type=EventType.SESSION_STARTED,
            session_id="session-3",
            timestamp=datetime.now(timezone.utc) - timedelta(days=1),
            user_id="user-3",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=StartSessionParameters(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
            )
        )
    ]

    for event in events:
        processor.process(event)


def test_category_viewed(repo):
    processor = CategoryViewedProcessor(repo)
    events = [
        Event(
            event_id="test1",
            event_type=EventType.CATEGORY_VIEWED,
            session_id="session-1",
            timestamp=datetime.now(timezone.utc),
            user_id="user-1",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=CategoryParameters(
                category=category1
            )
        ),
        Event(
            event_id="test2",
            event_type=EventType.CATEGORY_VIEWED,
            session_id="session-2",
            timestamp=datetime.now(timezone.utc),
            user_id="user-2",
            location=Location(
                country="US",
                state="State",
                city="City",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=CategoryParameters(
                category=category2
            )
        ),
        Event(
            event_id="test3",
            event_type=EventType.CATEGORY_VIEWED,
            session_id="session-3",
            timestamp=datetime.now(timezone.utc) - timedelta(days=1),
            user_id="user-3",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=CategoryParameters(
                category=category1
            )
        ),
        Event(
            event_id="test3",
            event_type=EventType.CATEGORY_VIEWED,
            session_id="session-3",
            timestamp=datetime.now(timezone.utc) + timedelta(hours=1),
            user_id="user-3",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=CategoryParameters(
                category=category2
            )
        )
    ]

    for event in events:
        processor.process(event)


def test_product_viewed(repo):
    processor = ProductViewedProcessor(repo)
    events = [
        Event(
            event_id="test1",
            event_type=EventType.PRODUCT_VIEWED,
            session_id="session-1",
            timestamp=datetime.now(timezone.utc),
            user_id="user-1",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=ProductParameters(
                product=product1
            )
        ),
        Event(
            event_id="test2",
            event_type=EventType.PRODUCT_VIEWED,
            session_id="session-2",
            timestamp=datetime.now(timezone.utc),
            user_id="user-2",
            location=Location(
                country="US",
                state="State",
                city="City",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=ProductParameters(
                product=product2
            )
        ),
        Event(
            event_id="test3",
            event_type=EventType.PRODUCT_VIEWED,
            session_id="session-3",
            timestamp=datetime.now(timezone.utc) - timedelta(days=1),
            user_id="user-3",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=ProductParameters(
                product=product1
            )
        ),
        Event(
            event_id="test3",
            event_type=EventType.PRODUCT_VIEWED,
            session_id="session-3",
            timestamp=datetime.now(timezone.utc) + timedelta(hours=1),
            user_id="user-3",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=ProductParameters(
                product=product2
            )
        )
    ]

    for event in events:
        processor.process(event)


def test_added_to_cart(repo):
    processor = ProductAddedToCartProcessor(repo)
    events = [
        Event(
            event_id="test1",
            event_type=EventType.PRODUCT_ADDED_TO_CART,
            session_id="session-1",
            timestamp=datetime.now(timezone.utc),
            user_id="user-1",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=CartParameters(
                product=product1,
                quantity=45
            )
        ),
        Event(
            event_id="test2",
            event_type=EventType.PRODUCT_ADDED_TO_CART,
            session_id="session-2",
            timestamp=datetime.now(timezone.utc),
            user_id="user-2",
            location=Location(
                country="US",
                state="State",
                city="City",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=CartParameters(
                product=product2,
                quantity=23
            )
        ),
        Event(
            event_id="test3",
            event_type=EventType.PRODUCT_ADDED_TO_CART,
            session_id="session-3",
            timestamp=datetime.now(timezone.utc) - timedelta(days=1),
            user_id="user-3",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=CartParameters(
                product=product1,
                quantity=34
            )
        ),
        Event(
            event_id="test3",
            event_type=EventType.PRODUCT_ADDED_TO_CART,
            session_id="session-3",
            timestamp=datetime.now(timezone.utc) + timedelta(hours=1),
            user_id="user-3",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=CartParameters(
                product=product2,
                quantity=45
            )
        )
    ]

    for event in events:
        processor.process(event)


def test_remove_from_cart(repo):
    processor = ProductRemovedFromCartProcessor(repo)
    events = [
        Event(
            event_id="test1",
            event_type=EventType.PRODUCT_REMOVED_FROM_CART,
            session_id="session-1",
            timestamp=datetime.now(timezone.utc),
            user_id="user-1",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=CartParameters(
                product=product1,
                quantity=21
            )
        ),
        Event(
            event_id="test2",
            event_type=EventType.PRODUCT_REMOVED_FROM_CART,
            session_id="session-2",
            timestamp=datetime.now(timezone.utc),
            user_id="user-2",
            location=Location(
                country="US",
                state="State",
                city="City",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=CartParameters(
                product=product2,
                quantity=12
            )
        ),
        Event(
            event_id="test3",
            event_type=EventType.PRODUCT_REMOVED_FROM_CART,
            session_id="session-3",
            timestamp=datetime.now(timezone.utc) - timedelta(days=1),
            user_id="user-3",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=CartParameters(
                product=product1,
                quantity=3
            )
        ),
        Event(
            event_id="test3",
            event_type=EventType.PRODUCT_REMOVED_FROM_CART,
            session_id="session-3",
            timestamp=datetime.now(timezone.utc) + timedelta(hours=1),
            user_id="user-3",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=CartParameters(
                product=product2,
                quantity=23
            )
        )
    ]

    for event in events:
        processor.process(event)

def test_purchase(repo):
    processor = PurchaseProcessor(repo)
    events = [
        Event(
            event_id="test1",
            event_type=EventType.PURCHASE,
            session_id="session-1",
            timestamp=datetime.now(timezone.utc),
            user_id="user-1",
            location=Location(
                country="IT",
                state="Lombardia",
                city="Milano",
                latitude=-3.460597,
                longitude=121.756339
            ),
            parameters=PurchaseParameters(
                items=[
                    PurchaseItem(
                        product=product1,
                        quantity=45 - 21,
                        subtotal=product1.price * (45 - 21)
                    )
                ],
                total_amount=(product1.price * (45 - 21)) - 50 + 25,
                discount_amount=50,
                shipping_address=Location(
                    country="IT",
                    state="Lombardia",
                    city="Milano",
                    latitude=-3.460597,
                    longitude=121.756339
                ),
                shipping_cost=25,
                payment_method=payment_method1,
                estimated_delivery_date=datetime.now(timezone.utc) + timedelta(days=10)
            )
        ),
    ]

    processor.process(events[0])

with FirebaseRepository(config.GOOGLE_APPLICATION_CREDENTIALS) as repository:
    test_session_started(repository)
    test_category_viewed(repository)
    test_product_viewed(repository)
    test_added_to_cart(repository)
    test_remove_from_cart(repository)
    test_purchase(repository)