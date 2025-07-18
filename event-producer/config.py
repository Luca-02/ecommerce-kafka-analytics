from pydantic import BaseModel


class EventProbabilities(BaseModel):
    add_to_cart: float = 0.5
    remove_from_cart: float = 0.25
    purchase: float = 0.75
    wishlist: float = 0.3
    share: float = 0.1