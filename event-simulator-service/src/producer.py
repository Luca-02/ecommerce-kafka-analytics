import sys
import time

from kafka import KafkaProducer
from kafka.errors import KafkaError
from loguru import logger

from .models import Event

CONNECTION_MAX_ATTEMPTS = 10
CONNECTION_RETRY_DELAY_SECONDS = 5

lambda_encoder = lambda x: x.encode('utf-8') if x else None


class Producer:
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer_config = {
            'client_id': 'event-simulator-service',
            'bootstrap_servers': self.bootstrap_servers,
            'key_serializer': lambda_encoder,
            'value_serializer': lambda_encoder,
            'acks': 'all',
            'retries': 5,
            'retry_backoff_ms': 1000,
            'batch_size': 32 * 1024, # 32KB
            'linger_ms': 10,
            'compression_type': 'gzip',
            'request_timeout_ms': 30000,
            'delivery_timeout_ms': 120000
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
        logger.info(f"[Kafka] Producing event: {event}")
        try:
            event_data = event.model_dump_json()
            self.producer.send(
                topic=self.topic,
                key=event.user_id,
                value=event_data
            )
        except KafkaError as e:
            logger.error(f"Kafka error during event production: {e}")
        except Exception as e:
            logger.error(f"General error during event production: {e}")

    def close(self):
        logger.info("[Kafka] Closing producer...")
        if self.producer:
            try:
                self.producer.flush(timeout=30)
                self.producer.close(timeout=10)
            except Exception as e:
                logger.error(f"Error during producer close: {e}")
        logger.info("[Kafka] Producer closed cleanly!")
