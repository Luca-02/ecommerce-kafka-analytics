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


class Category(BaseModel):
    id: str
    name: str


class Product(BaseModel):
    id: str
    name: str
    category: Category
    price: float
    currency: str


class PaymentMethod(BaseModel):
    id: str
    name: str


class EventType(Enum):
    SESSION_STARTED = "session_started"
    CATEGORY_VIEWED = "category_viewed"
    PRODUCT_VIEWED = "product_viewed"
    PRODUCT_ADDED_TO_CART = "product_added_to_cart"
    PRODUCT_REMOVED_FROM_CART = "product_removed_from_cart"
    PURCHASE = "purchase"
    SESSION_ENDED = "session_ended"


class StartSessionParameters(BaseModel):
    user_agent: str


class CategoryParameters(BaseModel):
    category: Category


class ProductParameters(BaseModel):
    product: Product


class CartParameters(BaseModel):
    product: Product
    quantity: int


class PurchaseItem(BaseModel):
    product: Product
    quantity: int
    subtotal: float


class PurchaseParameters(BaseModel):
    items: list[PurchaseItem]
    total_amount: float
    discount_amount: float
    shipping_address: Location
    shipping_cost: float
    payment_method: PaymentMethod
    estimated_delivery_date: datetime


class EndSessionParameters(BaseModel):
    seconds_duration: int


EventParameters = Union[
    StartSessionParameters,
    CategoryParameters,
    ProductParameters,
    CartParameters,
    PurchaseParameters,
    EndSessionParameters
]


class Event(BaseModel):
    event_id: str
    event_type: EventType
    session_id: str
    timestamp: datetime
    user_id: str
    location: Location
    parameters: EventParameters | None = None
