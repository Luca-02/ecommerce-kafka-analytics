import json
import logging
from typing import Dict

from model import Product, User


def __load_data(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"Error: File '{filename}' not found. Please ensure it's in the correct directory.")
        return []
    except json.JSONDecodeError:
        logging.error(f"Error: Could not decode JSON from '{filename}'. Check file format.")
        return []


def _load_users(filename) -> Dict[int, User]:
    raw_users = __load_data(filename)
    return {user["user_id"]: User(**user) for user in raw_users}


def _load_products(filename) -> Dict[int, Product]:
    raw_products = __load_data(filename)
    return {product["product_id"]: Product(**product) for product in raw_products}


class Repository:
    def __init__(
        self,
        users_file='mock_users_50.json',
        products_file='mock_products_100.json',
    ):
        self.event_types = [
            "product_viewed",
            "product_added_to_cart",
            "product_removed_from_cart",
            "product_purchased"
        ]
        self.users = _load_users(users_file)
        self.products = _load_products(products_file)

    def get_user_by_id(self, user_id: int) -> User | None:
        return self.users.get(user_id)

    def get_product_by_id(self, product_id: int) -> Product | None:
        return self.products.get(product_id)
