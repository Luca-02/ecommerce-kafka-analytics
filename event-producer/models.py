from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    id: int
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
    id: int
    name: str
    category: str
    price: float
    currency: str


class Event(BaseModel):
    event_type: str
    session_id: str
    timestamp: datetime
    user_id: int
    location: Location
    metadata: dict = {}