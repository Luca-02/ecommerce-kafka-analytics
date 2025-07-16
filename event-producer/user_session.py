import random
import uuid
from datetime import datetime

from models import Event, Location, Product, User


class UserSession:
    def __init__(self, user: User, location: Location):
        self.user_id: int = user.id
        self.location: Location = location
        self.session_id: str | None = None
        self.events: list[Event] = []
        self.cart: dict[int, dict] = {}

    def session_started(self):
        self.session_id = str(uuid.uuid4())
        self.events.append(Event(
            event_type="session_started",
            session_id=self.session_id,
            timestamp=datetime.now(),
            user_id=self.user_id,
            location=self.location
        ))

    def session_ended(self):
        self.events.append(Event(
            event_type="session_ended",
            session_id=self.session_id,
            timestamp=datetime.now(),
            user_id=self.user_id,
            location=self.location
        ))
        self.session_id = None

    def category_viewed(self, category: str):
        self.events.append(Event(
            event_type="category_viewed",
            session_id=self.session_id,
            timestamp=datetime.now(),
            user_id=self.user_id,
            location=self.location,
            metadata={
                "category": category
            }
        ))

    def product_viewed(self, product: Product):
        self.events.append(Event(
            event_type="product_viewed",
            session_id=self.session_id,
            timestamp=datetime.now(),
            user_id=self.user_id,
            location=self.location,
            metadata={
                "products": product
            }
        ))

    def product_added_to_cart(self, product: Product, quantity: int):
        if product.id in self.cart:
            self.cart[product.id]["quantity"] += quantity
        else:
            self.cart[product.id] = {
                "product": product,
                "quantity": quantity
            }

        self.events.append(Event(
            event_type="product_added_to_cart",
            session_id=self.session_id,
            timestamp=datetime.now(),
            user_id=self.user_id,
            location=self.location,
            metadata={
                "product": product,
                "quantity": quantity
            }
        ))

    def product_removed_from_cart(self, product: Product, quantity: int):
        if product.id in self.cart:
            current_qty = self.cart[product.id]["quantity"]
            new_qty = current_qty - quantity
            if new_qty <= 0:
                del self.cart[product.id]
            else:
                self.cart[product.id]["quantity"] = new_qty

        self.events.append(Event(
            event_type="product_removed_from_cart",
            session_id=self.session_id,
            timestamp=datetime.now(),
            user_id=self.user_id,
            location=self.location,
            metadata={
                "product": product,
                "quantity": quantity
            }
        ))

    def purchase(self):
        total_amount = sum(item["product"].price * item["quantity"] for item in self.cart.values())
        self.events.append(Event(
            event_type="purchase",
            session_id=self.session_id,
            timestamp=datetime.now(),
            user_id=self.user_id,
            location=self.location,
            metadata={
                "items": [
                    {
                        "product": item["product"],
                        "quantity": item["quantity"],
                        "subtotal": round(item["product"].price * item["quantity"], 2)
                    }
                    for item in self.cart.values()
                ],
                "total_amount": round(total_amount, 2)
            }
        ))
        self.cart.clear()

    def get_and_clear_events(self) -> list[Event]:
        events = self.events
        self.events = []
        return events

    def simulate(self, view_products_per_category: dict[str, list[Product]]):
        # Start session
        self.session_started()

        # View categories
        for category, products in view_products_per_category.items():
            self.category_viewed(category)

            # View products
            for product in products:
                self.product_viewed(product)

                # Add to cart with 50% probability with a random quantity from 1 to 5
                if random.random() < 0.5:
                    self.product_added_to_cart(product, random.randint(1, 5))

        for item in self.cart.values():
            # Remove random quantity from cart with 25% probability
            if random.random() < 0.25:
                quantity_to_remove = random.randint(1, item["quantity"])
                self.product_removed_from_cart(item["quantity"], random.randint(1, quantity_to_remove))

        # Purchase cart with 75% probability
        if self.cart and random.random() < 0.75:
            self.purchase()

        # End session
        self.session_ended()
