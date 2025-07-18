from datetime import datetime
from enum import Enum
from typing import Union

from pydantic import BaseModel


class User(BaseModel):
    id: str
    name: str
    username: str
    email: str


class Location(BaseModel):
    country: str
    state: str
    city: str
    latitude: float
    longitude: float


class Product(BaseModel):
    id: str
    name: str
    category: str
    price: float
    currency: str


class EventType(Enum):
    SESSION_STARTED = "session_started"
    SESSION_ENDED = "session_ended"
    CATEGORY_VIEWED = "category_viewed"
    PRODUCT_VIEWED = "product_viewed"
    PRODUCT_ADDED_TO_CART = "product_added_to_cart"
    PRODUCT_REMOVED_FROM_CART = "product_removed_from_cart"
    PURCHASE = "purchase"


class StartSessionMetadata(BaseModel):
    user_agent: str


class EndSessionMetadata(BaseModel):
    seconds_duration: int


class CategoryMetadata(BaseModel):
    category: str


class ProductMetadata(BaseModel):
    product: Product


class CartMetadata(BaseModel):
    product: Product
    quantity: int


class PurchaseItem(BaseModel):
    product: Product
    quantity: int
    subtotal: float


class PurchaseMetadata(BaseModel):
    items: list[PurchaseItem]
    total_amount: float
    discount_amount: float
    shipping_address: Location
    shipping_cost: float
    payment_method: str
    estimated_delivery_date: datetime


EventMetadata = Union[
    StartSessionMetadata,
    EndSessionMetadata,
    CategoryMetadata,
    ProductMetadata,
    CartMetadata,
    PurchaseMetadata
]


class Event(BaseModel):
    event_type: EventType
    session_id: str
    timestamp: datetime
    user_id: str
    location: Location
    metadata: EventMetadata | None = None
