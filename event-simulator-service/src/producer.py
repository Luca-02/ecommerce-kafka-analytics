from confluent_kafka import KafkaException, SerializingProducer
from confluent_kafka.error import KeySerializationError, ValueSerializationError
from confluent_kafka.serialization import StringSerializer

from shared.logger import get_logger
from shared.models import Event


class Producer:
    """
    Kafka producer for sending events to a Kafka topic.
    """

    def __init__(
        self,
        process_id: int,
        bootstrap_servers: str
    ):
        self._logger = get_logger(component=f'producer-{process_id}')
        self._bootstrap_servers = bootstrap_servers
        self._config = {
            "client.id": f"event-simulator-service",
            "bootstrap.servers": self._bootstrap_servers,
            "key.serializer": StringSerializer(),
            "value.serializer": StringSerializer(),
            "compression.type": "gzip",
            "acks": "all",
            "retries": 10
        }
        self._producer: SerializingProducer | None = None

        # # Se serve autenticazione SASL/SSL
        # if security_protocol != "PLAINTEXT":
        #     self.producer_config["security.protocol"] = security_protocol
        #     if sasl_mechanism:
        #         self.producer_config["sasl.mechanisms"] = sasl_mechanism
        #     if sasl_username and sasl_password:
        #         self.producer_config["sasl.username"] = sasl_username
        #         self.producer_config["sasl.password"] = sasl_password

    def __enter__(self):
        self._connect_to_kafka()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()

    def _connect_to_kafka(self):
        """
        Connects to Kafka using the provided configuration.

        :return: True if connection was successful, False otherwise.
        """
        if self._producer:
            self._logger.info(f"Already connected to Kafka.")

        try:
            self._producer = SerializingProducer(self._config)
            self._logger.info(f"Connected to Kafka through: {self._bootstrap_servers}")
        except Exception as e:
            self._logger.error(f"Error during connection to Kafka: {e}")

    def _close(self):
        """
        Closes the producer and flushes any remaining events.
        """
        self._logger.info(f"Closing producer...")
        if self._producer:
            try:
                self._producer.flush(timeout=30)
                self._logger.info(f"Producer closed cleanly!")
            except Exception as e:
                self._logger.error(f"Error during producer close: {e}")
            finally:
                self._producer = None

    def _delivery_report(self, err, msg):
        """
        Callback for delivery report.
        """
        if err is not None:
            self._logger.error(f"Error during message delivery: {err}")
        else:
            self._logger.debug(
                f"Message delivered to topic {msg.topic()} partition [{msg.partition()}] offset {msg.offset()}"
            )

    def produce(self, topic: str, event: Event):
        """
        Produces an event to the Kafka topic.

        :param event: The event to produce.
        :param topic: The topic to produce the event to.
        """
        if self._producer is None:
            self._logger.error(f"Producer is not connected to Kafka.")
            return

        try:
            self._logger.info(f"Producing event: {event}")
            self._producer.produce(
                topic=topic,
                key=event.session_id,
                value=event.model_dump_json(),
                on_delivery=self._delivery_report
            )
            # Wait up to 1 second for events. Callbacks will be invoked during
            # this method call if the message is acknowledged.
            self._producer.poll(timeout=1.0)
        except BufferError as e:
            self._logger.error(f"Internal producer message queue is full, event discarded: {e}")
        except KeySerializationError as e:
            self._logger.error(f"Kafka message key serialization error: {e}")
        except ValueSerializationError as e:
            self._logger.error(f"Kafka message value serialization error: {e}")
        except KafkaException as e:
            self._logger.error(f"Kafka error during event production: {e}")
        except Exception as e:
            self._logger.error(f"General error during event production: {e}")
