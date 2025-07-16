from models import Event
from repository import Repository
from user_session import UserSession

class Simulator:
    def __init__(self, repository: Repository = Repository()):
        self.repository = repository

    def simulate_user_session(self) -> list[Event]:
        user, location = self.repository.get_random_user()
        user_session = UserSession(user, location)
        view_products_per_category = self.repository.get_products_per_category_sample()
        user_session.simulate(view_products_per_category)
        events = user_session.get_and_clear_events()
        return events
