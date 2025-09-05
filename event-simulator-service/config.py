import os

from dotenv import load_dotenv

load_dotenv()

# Data path
DATA_PATH = os.getenv('DATA_PATH', './data')

# Kafka
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:9093')
KAFKA_TOPIC = os.getenv('KAFKA_EVENT_TOPIC', 'e-commerce-events')
# KAFKA_USERNAME = os.getenv('KAFKA_USERNAME', 'producerUser')
# KAFKA_PASSWORD = os.getenv('KAFKA_PASSWORD', 'producerPass')
# SSL_CAFILE = os.getenv('SSL_CAFILE', '/certs/ca-cert.pem')
# SSL_CERTFILE = os.getenv('SSL_CERTFILE', '/certs/kafka-cert.pem')
# SSL_KEYFILE = os.getenv('SSL_KEYFILE', '/certs/kafka-key.pem')

# Interval between user sessions in seconds
MIN_SESSION_INTERVAL_SECONDS = float(os.getenv('MIN_SESSION_INTERVAL_SECONDS', 1))
MAX_SESSION_INTERVAL_SECONDS = float(os.getenv('MAX_SESSION_INTERVAL_SECONDS', 5))

# Interval between events in seconds
MIN_EVENT_INTERVAL_SECONDS = float(os.getenv('MIN_EVENT_INTERVAL_SECONDS', 1))
MAX_EVENT_INTERVAL_SECONDS = float(os.getenv('MAX_EVENT_INTERVAL_SECONDS', 5))

# Probabilities
ADD_TO_CART_PROBABILITY = 0.5
REMOVE_FROM_CART_PROBABILITY = 0.25
PURCHASE_PROBABILITY = 0.75
DISCOUNT_PROBABILITY = 0.1

# Quantity limits
MIN_CART_QUANTITY = 1
MAX_CART_QUANTITY = 5

# Shipping
MIN_SHIPPING_COST = 0
MAX_SHIPPING_COST = 15.0

# Delivery
MIN_DELIVERY_DAYS = 2
MAX_DELIVERY_DAYS = 14
