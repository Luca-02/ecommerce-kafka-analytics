import os

from dotenv import load_dotenv

load_dotenv()

# Kafka
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:9092')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'analytics-service')
KAFKA_EVENT_TOPIC = os.getenv('KAFKA_EVENT_TOPIC', 'e-commerce-events')
KAFKA_SSL_CA_LOCATION = os.getenv('KAFKA_SSL_CA_LOCATION')
KAFKA_SASL_USERNAME = os.getenv('KAFKA_SASL_USERNAME')
KAFKA_SASL_PASSWORD = os.getenv('KAFKA_SASL_PASSWORD')

# Number of worker threads
WORKER_PROCESS_NUMBER = int(os.getenv('WORKER_PROCESS_NUMBER', 1))

# Firebase
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
