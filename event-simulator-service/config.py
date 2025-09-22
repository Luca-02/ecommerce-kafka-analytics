import os

from dotenv import load_dotenv

bool_map = {"true": True, "false": False}

load_dotenv()

# Data path
DATA_PATH = os.getenv('DATA_PATH', './data')

# Kafka
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:9093')
KAFKA_EVENT_TOPIC = os.getenv('KAFKA_EVENT_TOPIC', 'e-commerce-events')
KAFKA_SSL_CA_LOCATION = os.getenv('KAFKA_SSL_CA_LOCATION')
KAFKA_SSL_CHECK_HOSTNAME = os.getenv('KAFKA_SSL_CHECK_HOSTNAME')
if KAFKA_SSL_CHECK_HOSTNAME:
    KAFKA_SSL_CHECK_HOSTNAME = bool_map.get(os.getenv('KAFKA_SSL_CHECK_HOSTNAME').strip().lower(), False)
else:
    KAFKA_SSL_CHECK_HOSTNAME = False
KAFKA_SASL_USERNAME = os.getenv('KAFKA_SASL_USERNAME')
KAFKA_SASL_PASSWORD = os.getenv('KAFKA_SASL_PASSWORD')

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
DISCOUNT_PROBABILITY = float(os.getenv('DISCOUNT_PROBABILITY', 0.25))

# Quantity limits
MIN_CART_QUANTITY = int(os.getenv('MIN_CART_QUANTITY', 1))
MAX_CART_QUANTITY = int(os.getenv('MAX_CART_QUANTITY', 5))

# Shipping cost
MIN_SHIPPING_COST = float(os.getenv('MIN_SHIPPING_COST', 0))
MAX_SHIPPING_COST = float(os.getenv('MAX_SHIPPING_COST', 15.0))

# Delivery days
MIN_DELIVERY_DAYS = int(os.getenv('MIN_DELIVERY_DAYS', 2))
MAX_DELIVERY_DAYS = int(os.getenv('MAX_DELIVERY_DAYS', 14))
