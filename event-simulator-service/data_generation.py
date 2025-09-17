import json
import os
import random
import uuid

from faker import Faker

fake = Faker('en_US')

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 Chrome/118.0.5993.90 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; SAMSUNG SM-G991B) AppleWebKit/537.36 Chrome/112.0.0.0 Mobile Safari/537.36"
]

PAYMENTS_METHODS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Card"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Gift Card"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "PayPal"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Crypto"
    }
]

CATEGORIES = [
    {
        "id": str(uuid.uuid4()),
        "name": "Shoes"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Clothing"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Accessories"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Electronics"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Home"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Sports"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Toys"
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Beauty"
    }
]

data_path = os.getenv("DATA_PATH", "./data")

user_agents_path = os.path.join(data_path, "user_agents.json")
payments_methods_path = os.path.join(data_path, "payment_methods.json")
categories_path = os.path.join(data_path, "categories.json")
users_path = os.path.join(data_path, "users.json")
products_path = os.path.join(data_path, "products.json")


def generate_users_en(n=25):
    users = []
    for i in range(n):
        user_id = str(uuid.uuid4())
        users.append({
            "id": user_id,
            "name": fake.name(),
            "username": fake.user_name(),
            "email": fake.email(),
            "location": {
                "country": fake.country_code(),
                "state": fake.state(),
                "city": fake.city(),
                "latitude": float(fake.latitude()),
                "longitude": float(fake.longitude())
            }
        })
    return users


def generate_products_en(n=100):
    products = []
    for i in range(n):
        products.append({
            "id": str(uuid.uuid4()),
            "name": fake.sentence(nb_words=random.randint(2, 5)),
            "category": random.choice(CATEGORIES),
            "price": round(random.uniform(10, 300), 2),
            "currency": "USD"
        })
    return products


def write_json(file_path, data):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    generated_users = generate_users_en(25)
    generated_products = generate_products_en(100)

    write_json(categories_path, CATEGORIES)
    write_json(user_agents_path, USER_AGENTS)
    write_json(payments_methods_path, PAYMENTS_METHODS)
    write_json(users_path, generated_users)
    write_json(products_path, generated_products)
