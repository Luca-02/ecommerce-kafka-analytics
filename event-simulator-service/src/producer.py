import sys

from confluent_kafka import KafkaException, SerializingProducer
from confluent_kafka.error import KeySerializationError, ValueSerializationError
from confluent_kafka.serialization import StringSerializer

from .logger_utils import get_logger
from .models import Event


class Producer:
    """
    Kafka producer for sending events to a Kafka topic.
    """

    def __init__(
        self,
        process_id: int,
        bootstrap_servers: str
    ):
        self.logger = get_logger(component=f'producer-{process_id}')
        self.bootstrap_servers = bootstrap_servers
        self.config = {
            "client.id": f"event-simulator-service",
            "bootstrap.servers": self.bootstrap_servers,
            "key.serializer": StringSerializer(),
            "value.serializer": StringSerializer(),
            "compression.type": "gzip",
            "acks": "all",
            "retries": 10
        }

        # # Se serve autenticazione SASL/SSL
        # if security_protocol != "PLAINTEXT":
        #     self.producer_config["security.protocol"] = security_protocol
        #     if sasl_mechanism:
        #         self.producer_config["sasl.mechanisms"] = sasl_mechanism
        #     if sasl_username and sasl_password:
        #         self.producer_config["sasl.username"] = sasl_username
        #         self.producer_config["sasl.password"] = sasl_password

        self.producer: SerializingProducer | None = None

    def _delivery_report(self, err, msg):
        """
        Callback for delivery report.
        """
        if err is not None:
            self.logger.error(f"Error during message delivery: {err}")
        else:
            self.logger.debug(
                f"Message delivered to topic {msg.topic()} partition [{msg.partition()}] offset {msg.offset()}"
            )

    def connect_to_kafka(self) -> bool:
        """
        Connects to Kafka using the provided configuration.

        :return: True if connection was successful, False otherwise.
        """
        if self.producer:
            self.logger.info(f"Already connected to Kafka.")
            return True

        try:
            self.producer = SerializingProducer(self.config)
            self.logger.info(f"Connected to Kafka through: {self.bootstrap_servers}")
            return True
        except Exception as e:
            self.logger.error(f"Error during connection to Kafka: {e}")
            return False

    def produce(self, topic: str, event: Event):
        """
        Produces an event to the Kafka topic.

        :param event: The event to produce.
        :param topic: The topic to produce the event to.
        """
        if self.producer is None:
            self.logger.error(f"Producer is not connected to Kafka.")
            return

        try:
            self.logger.info(f"Producing event: {event}")
            self.producer.produce(
                topic=topic,
                key=event.session_id,
                value=event.model_dump_json(),
                on_delivery=self._delivery_report
            )
            # Wait up to 1 second for events. Callbacks will be invoked during
            # this method call if the message is acknowledged.
            self.producer.poll(timeout=1.0)
        except BufferError as e:
            self.logger.error(f"Internal producer message queue is full, event discarded: {e}")
        except KeySerializationError as e:
            self.logger.error(f"Kafka message key serialization error: {e}")
        except ValueSerializationError as e:
            self.logger.error(f"Kafka message value serialization error: {e}")
        except KafkaException as e:
            self.logger.error(f"Kafka error during event production: {e}")
        except Exception as e:
            self.logger.error(f"General error during event production: {e}")

    def close(self):
        """
        Closes the producer and flushes any remaining events.
        """
        self.logger.info(f"Closing producer...")
        if self.producer:
            try:
                self.producer.flush(timeout=30)
                self.logger.info(f"Producer closed cleanly!")
            except Exception as e:
                self.logger.error(f"Error during producer close: {e}")
            finally:
                self.producer = None
