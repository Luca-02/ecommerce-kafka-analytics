import json
import random

from models import Location, Product, User


def _load_data(filename: str):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)


def _load_entities(path: str, cls: any, key: lambda item: int) -> dict[int, any]:
    raw_data = _load_data(path)
    return {key(item): cls(**item) for item in raw_data}


class Repository:
    def __init__(
        self,
        users_path: str = './mock_data/users.json',
        locations_path: str = './mock_data/locations.json',
        products_path: str = './mock_data/products.json',
    ):
        self.users = _load_entities(users_path, User, lambda u: u["id"])
        self.locations = _load_entities(locations_path, Location, lambda l: l["user_id"])
        self.products = _load_entities(products_path, Product, lambda p: p["id"])
        self.categories = list({product.category for product in self.products.values()})

    def get_random_user(self) -> tuple[User, Location]:
        user = random.choice(list(self.users.values()))
        location = self.locations[user.id]
        return user, location

    def get_categories_sample(self, a: int = 0, b: int = 5) -> list[str]:
        num_categories = min(len(self.categories), random.randint(a, b))
        return random.sample(self.categories, num_categories)

    def get_products_sample_by_category(self, category: str, a: int = 0, b: int = 5) -> list[Product]:
        products_in_category = [p for p in self.products.values() if p.category == category]
        num_products = min(len(products_in_category), random.randint(a, b))
        return random.sample(products_in_category, num_products) if products_in_category else []
