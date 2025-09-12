import json
import os
import unittest
from unittest.mock import patch

from src.repository import MockRepository

user_agents = ["agent1", "agent2", "agent3"]
payment_methods = ["credit_card", "paypal"]
categories = ["Toys", "Home", "Shoes"]
users = [
    {
        "id": "300891aa-8d15-4992-bad9-b71460305008",
        "name": "Lorraine Martin",
        "username": "jamesjackson",
        "email": "susanhernandez@example.net",
        "location": {
            "country": "Canada",
            "state": "Iowa",
            "city": "Ericaton",
            "latitude": 83.4925405,
            "longitude": -23.015237
        }
    },
    {
        "id": "d1332a4a-946f-403e-97cd-3c604a06bced",
        "name": "Samuel Kelly",
        "username": "donna12",
        "email": "buckanne@example.com",
        "location": {
            "country": "Suriname",
            "state": "Illinois",
            "city": "Murrayborough",
            "latitude": 5.9415525,
            "longitude": 22.910158
        }
    },
]
products = [
    {
        "id": "95d67adf-128d-487f-ad1d-32638ad25875",
        "name": "Onto.",
        "category": "Toys",
        "price": 144.92,
        "currency": "USD"
    },
    {
        "id": "a1af60d6-9f2a-4e06-be20-63b2c3b013a4",
        "name": "Look.",
        "category": "Home",
        "price": 147.98,
        "currency": "USD"
    },
    {
        "id": "99b24f65-f306-44bb-a8fb-242af03e8839",
        "name": "Remain.",
        "category": "Shoes",
        "price": 11.73,
        "currency": "USD"
    }
]
mock_files = {
    "user_agents.json": json.dumps(user_agents),
    "payment_methods.json": json.dumps(payment_methods),
    "categories.json": json.dumps(categories),
    "users.json": json.dumps(users),
    "products.json": json.dumps(products)
}


def mock_load_data(filename):
    filename = os.path.basename(filename)
    return json.loads(mock_files[filename])


class TestRepository(unittest.TestCase):
    def setUp(self):
        patcher = patch("src.repository._load_data", side_effect=mock_load_data)
        self.mock_load_data_patch = patcher.start()
        self.addCleanup(patcher.stop)
        self.repo = MockRepository("mock/path")

    def test_repository_initialization(self):
        self.assertEqual(self.repo.user_agents, user_agents)
        self.assertEqual(self.repo.payment_methods, payment_methods)
        self.assertEqual(self.repo.categories, categories)
        self.assertEqual(len(self.repo.users), len(users))
        self.assertEqual(len(self.repo.locations), len(users))
        self.assertEqual(len(self.repo.products), len(products))

    def test_get_random_user_agent(self):
        agent = self.repo.get_random_user_agent()
        self.assertIn(agent, user_agents)

    def test_get_random_payment_method(self):
        method = self.repo.get_random_payment_method()
        self.assertIn(method, payment_methods)

    def test_get_categories_sample(self):
        sample = self.repo.get_categories_sample()
        for cat in sample:
            self.assertIn(cat, self.repo.categories)

    def test_get_random_user(self):
        user, location = self.repo.get_random_user()
        user_location = user.__dict__
        user_location["location"] = location.__dict__
        self.assertIn(user_location, users)

    def test_get_products_sample_by_category(self):
        for cat in categories:
            sample = self.repo.get_products_sample_by_category(cat)
            for product in sample:
                self.assertEqual(product.category, cat)

    def test_get_products_sample_by_category_not_exist(self):
        none = self.repo.get_products_sample_by_category("NotExist")
        self.assertEqual(none, [])
