import os

from dotenv import load_dotenv

load_dotenv()

# Data path
DATA_PATH = os.getenv('DATA_PATH', './data')

# Kafka
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:9093')
KAFKA_TOPIC = os.getenv('KAFKA_EVENT_TOPIC', 'e-commerce-events')

# Number of simulation processes
NUMBER_SIMULATION_PROCESSES = int(os.getenv('NUMBER_SIMULATION_PROCESSES', 1))

# Interval between user sessions in seconds
MIN_SESSION_INTERVAL_SECONDS = float(os.getenv('MIN_SESSION_INTERVAL_SECONDS', 1))
MAX_SESSION_INTERVAL_SECONDS = float(os.getenv('MAX_SESSION_INTERVAL_SECONDS', 10))

# Interval between events in seconds
MIN_EVENT_INTERVAL_SECONDS = float(os.getenv('MIN_EVENT_INTERVAL_SECONDS', 1))
MAX_EVENT_INTERVAL_SECONDS = float(os.getenv('MAX_EVENT_INTERVAL_SECONDS', 10))

# Probabilities
ADD_TO_CART_PROBABILITY = float(os.getenv('ADD_TO_CART_PROBABILITY', 0.5))
REMOVE_FROM_CART_PROBABILITY = float(os.getenv('REMOVE_FROM_CART_PROBABILITY', 0.25))
PURCHASE_PROBABILITY = float(os.getenv('PURCHASE_PROBABILITY', 0.75))
DISCOUNT_PROBABILITY = float(os.getenv('DISCOUNT_PROBABILITY', 0.1))

# Quantity limits
MIN_CART_QUANTITY = int(os.getenv('MIN_CART_QUANTITY', 1))
MAX_CART_QUANTITY = int(os.getenv('MAX_CART_QUANTITY', 5))

# Shipping cost
MIN_SHIPPING_COST = float(os.getenv('MIN_SHIPPING_COST', 0))
MAX_SHIPPING_COST = float(os.getenv('MAX_SHIPPING_COST', 15.0))

# Delivery days
MIN_DELIVERY_DAYS = int(os.getenv('MIN_DELIVERY_DAYS', 2))
MAX_DELIVERY_DAYS = int(os.getenv('MAX_DELIVERY_DAYS', 14))
