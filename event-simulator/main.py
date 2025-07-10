from functools import lru_cache

from fastapi import Depends, FastAPI

from event_service import EventService
from model import EventSkeleton, RandomEventInput
from repository import Repository

app = FastAPI()


@lru_cache
def get_repository() -> Repository:
    """
    Create a cache for the repository with @lru_cache to improve performance, instance the repository only once.
    """
    return Repository()


def get_event_service(repository: Repository = Depends(get_repository)) -> EventService:
    return EventService(repository)


@app.post("/view")
async def view(
    event_data: EventSkeleton,
    event_service: EventService = Depends(get_event_service)
):
    """
    Simulate a product view event.
    """
    event = event_service.process_event("product_viewed", event_data)
    return {
        "event": event
    }


@app.post("/add-to-cart")
async def add_to_cart(
    event_data: EventSkeleton,
    event_service: EventService = Depends(get_event_service)
):
    """
    Simulate a product add to cart event.
    """
    event = event_service.process_event("product_added_to_cart", event_data)
    return {
        "event": event
    }


@app.post("/remove-from-cart")
async def remove_from_cart(
    event_data: EventSkeleton,
    event_service: EventService = Depends(get_event_service)
):
    """
    Simulate a product remove from cart event.
    """
    event = event_service.process_event("product_removed_from_cart", event_data)
    return {
        "event": event
    }


@app.post("/purchase")
async def purchase(
    event_data: EventSkeleton,
    event_service: EventService = Depends(get_event_service)
):
    """
    Simulate a product purchase event.
    """
    event = event_service.process_event("product_purchased", event_data)
    return {
        "event": event
    }


@app.post("/generate-random-events")
async def generate_random_events(
    random_event_input: RandomEventInput,
    event_service: EventService = Depends(get_event_service)
):
    """
    Generates a specified number of random e-commerce events and publish them.
    """
    generated_events = event_service.generate_random_events(random_event_input)
    return {
        "number_of_events": len(generated_events),
        "events": generated_events
    }

# Run the app with uvicorn:
# uvicorn main:app --reload --port 8080
