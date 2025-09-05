import os

from dotenv import load_dotenv

load_dotenv()

# Kafka
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:9093')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'analytics-service')
KAFKA_TOPIC = os.getenv('KAFKA_EVENT_TOPIC', 'e-commerce-events')
