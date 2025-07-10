import logging
import random
from datetime import date
from datetime import datetime

from faker import Faker
from fastapi import HTTPException

from model import Event, EventSkeleton, RandomEventInput
from repository import Repository


class EventService:
    def __init__(self, repository: Repository):
        self.repository = repository

    def publish_event(self, event: Event):
        # TODO Here, in the future, we will add the logic to send the event to Kafka
        logging.info(f"{event.event_type.replace('_', ' ').capitalize()}: {event}")

    def process_event(self, event_name: str, event_data: EventSkeleton):
        """
        Process an event.

        :param event_name: The name of the event.
        :param event_data: The data of the event.
        :return: Success message if the event was processed.
        """
        user = self.repository.get_user_by_id(event_data.user_id)
        product = self.repository.get_product_by_id(event_data.product_id)

        if user is None:
            raise HTTPException(status_code=404, detail="User not found.")
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found.")

        event = Event(
            event_type=event_name,
            user=user,
            product=product,
            timestamp=datetime.now(),
            quantity=event_data.quantity
        )

        self.publish_event(event)

        return event

    def generate_random_events(self, random_event_input: RandomEventInput):
        """
        Generates a specified number of random e-commerce events and publish them.

        :param random_event_input: The input containing the number of events to generate and the start and end dates.
        :return: A list of generated events.
        """
        if random_event_input.num_events <= 0:
            raise HTTPException(status_code=400, detail="num_events must be a positive integer.")

        if (random_event_input.start_date and
            random_event_input.end_date and
            random_event_input.start_date > random_event_input.end_date):
            raise HTTPException(status_code=400, detail="start_datetime cannot be after end_datetime.")

        generated_events = []
        for _ in range(random_event_input.num_events):
            event = self.__generate_event(
                start_date=random_event_input.start_date,
                end_date=random_event_input.end_date
            )
            generated_events.append(event)
            self.publish_event(event)

        return generated_events

    def __generate_event(
        self,
        start_date: date | None = None,
        end_date: date | None = None
    ) -> Event:
        """
        Generates a random e-commerce event.

        :param start_date: Start date for the event, defaults to datetime(2020, 1, 1).
        :param end_date: End date for the event, defaults to datetime(2025, 1, 1).
        :return: the generated event.
        """
        fake = Faker('en_US')

        if start_date is None:
            start_date = datetime(2020, 1, 1)
        if end_date is None:
            end_date = datetime(2025, 1, 1)

        event_type = random.choice(self.repository.event_types)
        user = random.choice(list(self.repository.users.values()))
        product = random.choice(list(self.repository.products.values()))
        timestamp = fake.date_time_between(start_date=start_date, end_date=end_date)

        if event_type in ["product_added_to_cart", "product_removed_from_cart", "product_purchased"]:
            quantity = random.randint(1, 5)
            return Event(event_type=event_type, user=user, product=product, timestamp=timestamp, quantity=quantity)

        return Event(event_type=event_type, user=user, product=product, timestamp=timestamp)
