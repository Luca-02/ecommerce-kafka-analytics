import sys
import time

from kafka import KafkaProducer
from kafka.errors import KafkaError

from .logger_utils import get_logger
from .models import Event

CONNECTION_MAX_ATTEMPTS = 10
CONNECTION_RETRY_DELAY_SECONDS = 5

lambda_encoder = lambda x: x.encode('utf-8') if x else None


class Producer:
    def __init__(
        self,
        process_id: int,
        bootstrap_servers: str,
        topic: str
    ):
        self.producer: KafkaProducer | None = None
        self.logger = get_logger(component=f'producer-{process_id}')
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
            'batch_size': 32 * 1024,
            'linger_ms': 10,
            'compression_type': 'gzip',
            'request_timeout_ms': 30000,
            'delivery_timeout_ms': 120000
        }

    def connect_to_kafka(self):
        if self.producer is not None:
            self.logger.info(f"Already connected to Kafka.")
            return

        self.logger.info(f"Connecting to Kafka...")
        for attempt in range(CONNECTION_MAX_ATTEMPTS):
            try:
                self.producer = KafkaProducer(**self.producer_config)
                self.logger.info(f"Connected to Kafka through: {self.bootstrap_servers}")
                return
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < CONNECTION_MAX_ATTEMPTS - 1:
                    self.logger.info(f"Retrying in {CONNECTION_RETRY_DELAY_SECONDS} seconds...")
                    time.sleep(CONNECTION_RETRY_DELAY_SECONDS)
                else:
                    self.logger.error(f"Impossible to connect to Kafka after {CONNECTION_MAX_ATTEMPTS} attempts.")
                    sys.exit(1)

    def produce(self, event: Event):
        if self.producer is None:
            self.logger.error(f"Producer is not connected to Kafka.")
            return

        self.logger.info(f"Producing event: {event}")
        try:
            event_data = event.model_dump_json()
            self.producer.send(
                topic=self.topic,
                key=event.user_id,
                value=event_data
            )
        except KafkaError as e:
            self.logger.error(f"Kafka error during event production: {e}")
        except Exception as e:
            self.logger.error(f"General error during event production: {e}")

    def close(self):
        self.logger.info(f"Closing producer...")
        if self.producer:
            try:
                self.producer.flush(timeout=30)
                self.producer.close()
            except Exception as e:
                self.logger.error(f"Error during producer close: {e}")
        self.logger.info(f"Producer closed cleanly!")
