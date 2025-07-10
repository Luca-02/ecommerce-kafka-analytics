from datetime import date, datetime

from pydantic import BaseModel


class RandomEventInput(BaseModel):
    num_events: int = 1,
    start_date: date | None = None
    end_date: date | None = None


class User(BaseModel):
    user_id: int
    username: str
    email: str
    country: str
    city: str


class Product(BaseModel):
    product_id: int
    product_name: str
    category: str
    price: float
    currency: str


class EventSkeleton(BaseModel):
    user_id: int
    product_id: int
    quantity: int | None = None


class Event(BaseModel):
    event_type: str
    user: User
    product: Product
    timestamp: datetime
    quantity: int | None = None
