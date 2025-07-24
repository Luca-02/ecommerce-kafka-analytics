import json
import os
import random

from .models import Location, Product, User


def _load_data(filename: str):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def _load_users_locations(path: str) -> tuple[dict[str, User], dict[str, Location]]:
    raw_data = _load_data(path)
    users = {}
    locations = {}
    for item in raw_data:
        user_id = item["id"]
        location_data = item.pop("location")
        users[user_id] = User(**item)
        locations[user_id] = Location(**location_data)
    return users, locations


def _load_entities(path: str, cls: any, key: lambda item: int) -> dict[int, any]:
    raw_data = _load_data(path)
    return {key(item): cls(**item) for item in raw_data}


class Repository:
    def __init__(
        self,
        data_path: str
    ):
        self.user_agents = _load_data(os.path.join(data_path, "user_agents.json"))
        self.payments_methods = _load_data(os.path.join(data_path, "payment_methods.json"))
        self.categories = _load_data(os.path.join(data_path, "categories.json"))
        self.users, self.locations = _load_users_locations(os.path.join(data_path, "users.json"))
        self.products = _load_entities(os.path.join(data_path, "products.json"), Product, lambda p: p["id"])

    def get_random_user_agent(self):
        return random.choice(self.user_agents)

    def get_random_payment_method(self):
        return random.choice(self.payments_methods)

    def get_categories_sample(self, a: int = 1, b: int = 5) -> list[str]:
        num_categories = min(len(self.categories), random.randint(a, b))
        return random.sample(self.categories, num_categories)

    def get_random_user(self) -> tuple[User, Location]:
        user = random.choice(list(self.users.values()))
        location = self.locations[user.id]
        return user, location

    def get_products_sample_by_category(self, category: str, a: int = 1, b: int = 5) -> list[Product]:
        products_in_category = [p for p in self.products.values() if p.category == category]
        num_products = min(len(products_in_category), random.randint(a, b))
        return random.sample(products_in_category, num_products) if products_in_category else []
