import os

from dotenv import load_dotenv

bool_map = {"true": True, "false": False}

load_dotenv()

# Kafka
KAFKA_BROKERS = os.getenv('KAFKA_BROKERS', 'localhost:9092')
KAFKA_GROUP_ID = os.getenv('KAFKA_GROUP_ID', 'analytics-service')
KAFKA_EVENT_TOPIC = os.getenv('KAFKA_EVENT_TOPIC', 'e-commerce-events')
KAFKA_SSL_CA_LOCATION = os.getenv('KAFKA_SSL_CA_LOCATION')
KAFKA_SSL_CHECK_HOSTNAME = os.getenv('KAFKA_SSL_CHECK_HOSTNAME')
if KAFKA_SSL_CHECK_HOSTNAME:
    KAFKA_SSL_CHECK_HOSTNAME = bool_map.get(os.getenv('KAFKA_SSL_CHECK_HOSTNAME').strip().lower(), False)
else:
    KAFKA_SSL_CHECK_HOSTNAME = False
KAFKA_SASL_USERNAME = os.getenv('KAFKA_SASL_USERNAME')
KAFKA_SASL_PASSWORD = os.getenv('KAFKA_SASL_PASSWORD')

# Number of worker threads
WORKER_PROCESS_NUMBER = int(os.getenv('WORKER_PROCESS_NUMBER', 1))

# Firebase
GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
