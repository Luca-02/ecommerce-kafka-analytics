import sys
import time

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from loguru import logger

from .models import Event

CONNECTION_MAX_ATTEMPTS = 10
CONNECTION_RETRY_DELAY_SECONDS = 5

lambda_encoder = lambda x: x.encode('utf-8') if x else None


class Consumer:
    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topic: str
    ):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topic = topic
        self.consumer_config = {
            'client_id': 'analytics-service',
            'group_id': self.group_id,
            'bootstrap_servers': self.bootstrap_servers,
            'key_serializer': lambda_encoder,
            'value_serializer': lambda_encoder,
            'auto_offset_reset': 'earliest'
        }
        self.consumer = None

    def connect_to_kafka(self):
        if self.consumer is not None:
            logger.info("Already connected to Kafka.")
            return

        logger.info("Connecting to Kafka...")
        for attempt in range(CONNECTION_MAX_ATTEMPTS):
            try:
                self.consumer = KafkaConsumer(**self.consumer_config)
                logger.info(f"Connected to Kafka through: {self.bootstrap_servers}")
                return
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < CONNECTION_MAX_ATTEMPTS - 1:
                    logger.info(f"Retrying in {CONNECTION_RETRY_DELAY_SECONDS} seconds...")
                    time.sleep(CONNECTION_RETRY_DELAY_SECONDS)
                else:
                    logger.error(f"Impossible to connect to Kafka after {CONNECTION_MAX_ATTEMPTS} attempts.")
                    sys.exit(1)

    def consume_from_topic(self):
        if self.consumer is None:
            logger.error("Consumer is not connected to Kafka.")
            return

        # TODO
        pass


    def close(self):
        logger.info("[Kafka] Closing consumer...")
        if self.consumer:
            try:
                self.consumer.flush(timeout=30)
                self.consumer.close(timeout=10)
            except Exception as e:
                logger.error(f"Error during consumer close: {e}")
        logger.info("[Kafka] Consumer closed cleanly!")
