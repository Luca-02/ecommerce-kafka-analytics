import sys
import time

from kafka import KafkaProducer
from kafka.errors import KafkaError
from loguru import logger

from .models import Event

CONNECTION_MAX_ATTEMPTS = 10
CONNECTION_RETRY_DELAY_SECONDS = 5

lambda_encoder = lambda x: x.encode('utf-8') if x else None


def _on_send_success(record_metadata, event_data):
    logger.info(
        f"[Kafka] Event sent: topic={record_metadata.topic}, "
        f"partition={record_metadata.partition}, "
        f"offset={record_metadata.offset}, "
        f"message={event_data}"
    )


def _on_send_error(excp, event_data):
    logger.error(f"Kafka error for event {event_data}: {excp}")


class Producer:
    def __init__(
        self,
        bootstrap_servers: str,
        topic: str
    ):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer_config = {
            'bootstrap_servers': self.bootstrap_servers,
            'key_serializer': lambda_encoder,
            'value_serializer': lambda_encoder,
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
        logger.info(f"[Kafka] Producing event: {event}")
        try:
            event_data = event.model_dump_json()
            future = self.producer.send(
                topic=self.topic,
                key=event.user_id,
                value=event_data
            )
            future.add_callback(_on_send_success, event_data)
            future.add_errback(_on_send_error, event_data)
        except KafkaError as e:
            logger.error(f"Kafka error: {e}")
        except Exception as e:
            logger.error(f"General error: {e}")

    def close(self):
        logger.info("[Kafka] Flushing producer messages...")
        self.producer.flush()
        self.producer.close()
        logger.info("[Kafka] Producer closed cleanly!")
