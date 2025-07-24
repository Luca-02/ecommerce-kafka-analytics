import json
import sys
import time

from kafka import KafkaProducer
from kafka.errors import KafkaError
from loguru import logger

from config import KAFKA_BROKERS, KAFKA_TOPIC
from .models import Event

CONNECTION_MAX_ATTEMPTS = 10
CONNECTION_RETRY_DELAY_SECONDS = 5


class Producer:
    def __init__(self):
        self.bootstrap_servers = KAFKA_BROKERS.split(',')
        self.topic = KAFKA_TOPIC
        self.producer_config = {
            'bootstrap_servers': self.bootstrap_servers,
            'key_serializer': lambda x: x.encode('utf-8') if x else None,
            'value_serializer': lambda x: json.dumps(x).encode('utf-8'),
            'acks': 'all',
            'retries': 3,
            'compression_type': 'gzip'
            # TODO Uncomment and configure for SSL/SASL authentication
            # security_protocol="SASL_SSL",
            # ssl_cafile=SSL_CAFILE,
            # ssl_certfile=SSL_CERTFILE,
            # ssl_keyfile=SSL_KEYFILE,
            # sasl_mechanism="PLAIN",
            # sasl_plain_username=KAFKA_USERNAME,
            # sasl_plain_password=KAFKA_PASSWORD,
        }
        self.producer = None

    def connect_to_kafka(self):
        if self.producer is not None:
            logger.info("Already connected to Kafka.")
            return

        logger.info("Connecting to Kafka...")
        for attempt in range(CONNECTION_MAX_ATTEMPTS):
            try:
                self.producer = KafkaProducer(**self.producer_config)
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

    def produce(self, event: Event):
        try:
            # With user_id as key all the events for the same user will be in the same partition
            future = self.producer.send(
                topic=KAFKA_TOPIC,
                key=event.user_id,
                value=event.model_dump()
            )
            # Wait for the event to be sent
            record_metadata = future.get(timeout=10)
            logger.info(
                f"[Kafka] Event sent: topic={record_metadata.topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}, "
                f"message={event}"
            )
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
        except Exception as e:
            logger.error(f"General error: {e}")

    def close(self):
        logger.info("[Kafka] Flushing producer messages...")
        self.producer.flush()
        self.producer.close()
        logger.info("[Kafka] Producer closed cleanly!")
