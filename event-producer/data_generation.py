import json
import random

from faker import Faker

fake = Faker('en_US')
CATEGORIES = ["Shoes", "Clothing", "Accessories", "Electronics", "Home", "Sports", "Toys", "Beauty"]


def generate_users_en(n=25):
    users = []
    locations = []
    for i in range(n):
        users.append({
            "id": i + 1,
            "name": fake.name(),
            "username": fake.user_name(),
            "email": fake.email(),
        })
        locations.append({
            "user_id": i + 1,
            "country": fake.country(),
            "state": fake.state(),
            "city": fake.city(),
            "latitude": float(fake.latitude()),
            "longitude": float(fake.longitude())
        })
    return users, locations


def generate_products_en(n=100):
    products = []
    for i in range(n):
        products.append({
            "id": i + 1,
            "name": fake.sentence(nb_words=random.randint(2, 8)),
            "category": random.choice(CATEGORIES),
            "price": round(random.uniform(10, 300), 2),
            "currency": "USD"
        })
    return products


generated_users, generated_locations = generate_users_en(25)
generated_products = generate_products_en(100)

users_path = "./mock_data/users.json"
locations_path = "./mock_data/locations.json"
products_path = "./mock_data/products.json"

with open(users_path, "w") as f:
    json.dump(generated_users, f, indent=2, ensure_ascii=False)

with open(locations_path, "w") as f:
    json.dump(generated_locations, f, indent=2, ensure_ascii=False)

with open(products_path, "w") as f:
    json.dump(generated_products, f, indent=2, ensure_ascii=False)
