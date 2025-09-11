import json
import unittest

from src.models import Event

class Test(unittest.TestCase):
    def test(self):
        v = """
        {
            "event_type": "product_viewed",
            "session_id": "d766e187-d541-4cf9-8876-250cde908539",
            "timestamp": "2025-09-11T02:10:51.003855",
            "user_id": "92d84715-1ea9-45d0-aedc-e1d4eb7c8480",
            "location": {
                "country": "Tunisia",
                "state": "Indiana",
                "city": "Perezton",
                "latitude": 14.9553755,
                "longitude": -152.384479
            },
            "parameters": {
                "product": {
                    "id": "ac7d01f9-4026-4e06-9a46-3dd0ab39ca2a",
                    "name": "Customer.",
                    "category": "Home",
                    "price": 183.44,
                    "currency": "USD"
                },
                "quantity": 1
            }
        }
        """.strip()

        event = Event(**json.loads(v))
        print(v)
        print(event)
