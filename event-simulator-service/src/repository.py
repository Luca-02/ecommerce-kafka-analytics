import json
import os
import random

from shared.models import Category, Location, PaymentMethod, Product, User


def _load_data(path: str):
    """
    Load data from a JSON file.

    :param path: file path
    :return: loaded data
    """
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _load_users_locations(path: str) -> tuple[dict[str, User], dict[str, Location]]:
    """
    Load users and locations from a JSON file.

    :param path: file path
    :return: users and locations dictionaries
    """
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
    """
    Load entities from a JSON file.

    :param path: file path
    :param cls: entity class
    :param key: key function
    :return: entities dictionary
    """
    raw_data = _load_data(path)
    return {key(item): cls(**item) for item in raw_data}


class Repository:
    """
    Repository class for loading mock data from JSON files.
    """

    def __init__(
        self,
        data_path: str
    ):
        self._user_agents = _load_data(os.path.join(data_path, "user_agents.json"))
        self._payment_methods = _load_entities(
            os.path.join(data_path, "payment_methods.json"), PaymentMethod, lambda p: p["id"])
        self._categories = _load_entities(os.path.join(data_path, "categories.json"), Category, lambda c: c["id"])
        self._users, self._locations = _load_users_locations(os.path.join(data_path, "users.json"))
        self._products = _load_entities(os.path.join(data_path, "products.json"), Product, lambda p: p["id"])

    def get_random_user_agent(self) -> str:
        """
        Get a random user agent.

        :return: random user agent
        """
        return random.choice(self._user_agents)

    def get_random_payment_method(self) -> PaymentMethod:
        """
        Get a random payment method.

        :return: random payment method
        """
        return random.choice(list(self._payment_methods.values()))

    def get_random_user(self) -> tuple[User, Location]:
        """
        Get a random user and their location.

        :return: random user and location
        """
        user = random.choice(list(self._users.values()))
        location = self._locations[user.id]
        return user, location

    def get_categories_sample(self, a: int = 1, b: int = 5) -> list[Category]:
        """
        Get a random sample of categories.

        :param a: minimum number of categories (1 by default)
        :param b: maximum number of categories (5 by default)
        :return: random sample of categories
        """
        num_categories = min(len(self._categories), random.randint(a, b))
        return random.sample(list(self._categories.values()), num_categories)

    def get_products_sample_by_category(self, category: Category, a: int = 1, b: int = 5) -> list[Product]:
        """
        Get a random sample of products in a specific category.

        :param category: category of the products to sample
        :param a: minimum number of products (1 by default)
        :param b: maximum number of products (5 by default)
        :return: random sample of products in the category
        """
        products_in_category = [p for p in self._products.values() if p.category == category]
        num_products = min(len(products_in_category), random.randint(a, b))
        return random.sample(products_in_category, num_products) if products_in_category else []
