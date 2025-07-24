import os
import unittest
from unittest.mock import patch

from src.repository import Repository


class TestRepository(unittest.TestCase):
    def setUp(self):
        self.user_agents = ["agent1", "agent2", "agent3"]
        self.payment_methods = ["credit_card", "paypal"]
        self.categories = ["Toys", "Home", "Shoes"]
        self.users = [
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
        self.products = [
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

        self.mock_files = {
            "user_agents.json": self.user_agents,
            "payment_methods.json": self.payment_methods,
            "categories.json": self.categories,
            "users.json": self.users,
            "products.json": self.products
        }

    def mock_load_data(self, filename):
        filename = os.path.basename(filename)
        return self.mock_files[filename]

    def _mock_repository(self, mock_data):
        mock_data.side_effect = self.mock_load_data
        return Repository("mock/path")

    @patch("src.repository._load_data")
    def test_repository_initialization(self, mock_data):
        repo = self._mock_repository(mock_data)

        self.assertEqual(repo.user_agents, self.user_agents)
        self.assertEqual(repo.payments_methods, self.payment_methods)
        self.assertEqual(repo.categories, self.categories)
        self.assertEqual(len(repo.users), len(self.users))
        self.assertEqual(len(repo.locations), len(self.users))
        self.assertEqual(len(repo.products), len(self.products))

    @patch("src.repository._load_data")
    def test_get_random_user_agent(self, mock_data):
        repo = self._mock_repository(mock_data)
        agent = repo.get_random_user_agent()
        self.assertIn(agent, repo.user_agents)

    @patch("src.repository._load_data")
    def test_get_random_payment_method(self, mock_data):
        repo = self._mock_repository(mock_data)
        method = repo.get_random_payment_method()
        self.assertIn(method, repo.payments_methods)

    @patch("src.repository._load_data")
    def test_get_categories_sample(self, mock_data):
        repo = self._mock_repository(mock_data)
        sample = repo.get_categories_sample()
        for cat in sample:
            self.assertIn(cat, repo.categories)

    @patch("src.repository._load_data")
    def test_get_random_user(self, mock_data):
        repo = self._mock_repository(mock_data)
        user, location = repo.get_random_user()
        self.assertIsNotNone(user)
        self.assertIsNotNone(location)
        self.assertIn(user.id, repo.users)
        self.assertIn(user.id, repo.locations)

    @patch("src.repository._load_data")
    def test_get_products_sample_by_category(self, mock_data):
        repo = self._mock_repository(mock_data)
        for cat in repo.categories:
            sample = repo.get_products_sample_by_category(cat)
            for product in sample:
                self.assertEqual(product.category, cat)

    @patch("src.repository._load_data")
    def test_get_products_sample_by_category_not_exist(self, mock_data):
        repo = self._mock_repository(mock_data)
        none = repo.get_products_sample_by_category("NotExist")
        self.assertEqual(none, [])
