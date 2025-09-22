from confluent_kafka import DeserializingConsumer, KafkaError
from confluent_kafka.error import ConsumeError, KeyDeserializationError, ValueDeserializationError
from confluent_kafka.serialization import StringDeserializer

from shared.logger import get_logger
from .message_handler import MessageHandler


class Consumer:
    def __init__(
        self,
        message_handler: MessageHandler,
        bootstrap_servers: str,
        group_id: str,
        ssl_ca_location: str = None,
        ssl_check_hostname: bool = None,
        sasl_username: str = None,
        sasl_password: str = None
    ):
        self._logger = get_logger(component=f'consumer')
        self._bootstrap_servers = bootstrap_servers
        self._group_id = group_id
        self._message_handler = message_handler
        self._config = {
            "client.id": "analytics-service",
            "group.id": self._group_id,
            "bootstrap.servers": self._bootstrap_servers,
            "key.deserializer": StringDeserializer(),
            "value.deserializer": StringDeserializer(),
            "auto.offset.reset": "latest",
            'on_commit': self._commit_completed
        }
        if ssl_ca_location and sasl_username and sasl_password:
            self._config.update({
                'security.protocol': 'SASL_SSL',
                'sasl.mechanism': 'SCRAM-SHA-256',
                'ssl.ca.location': ssl_ca_location,
                'sasl.username': sasl_username,
                'sasl.password': sasl_password,
            })
            # Skip hostname validation in certificate
            if not ssl_check_hostname:
                self._config.update({
                    'ssl.endpoint.identification.algorithm': 'none'
                })
        self._poll_timeout_sec = 1.0
        self._consumer: DeserializingConsumer | None = None


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
        if self._consumer:
            self._logger.info("Already connected to Kafka.")

        try:
            self._consumer = DeserializingConsumer(self._config)
            self._logger.info(f"Connecting to Kafka through: {self._bootstrap_servers}")
        except Exception as e:
            self._logger.error(f"Error during connection to Kafka: {e}")

    def _close(self):
        """
        Closes the consumer stopping the consumption process.
        """
        self._logger.info("Closing consumer...")
        if self._consumer:
            try:
                if self._consumer:
                    self._consumer.close()
                    self._consumer = None
                self._logger.info("Consumer closed cleanly!")
            except Exception as e:
                self._logger.error(f"Error during consumer close: {e}")

    def _commit_completed(self, err, _):
        if err:
            self._logger.error(f"Error during commit: {err}")
        else:
            self._logger.info(f"Committed partition offsets")

    def _polling_process(self):
        """
        Polls for messages from Kafka and processes them.
        """
        try:
            msg = self._consumer.poll(timeout=1.0)
            if msg is None:
                return

            if msg.error() and msg.error().code() != KafkaError._PARTITION_EOF:  # End of partition event
                self._logger.error(f"Error during message processing: {msg.error()}")
            else:
                self._message_handler.handle(msg)
        except KeyDeserializationError as e:
            self._logger.error(f"Kafka message key deserialization error: {e}")
        except ValueDeserializationError as e:
            self._logger.error(f"Kafka message value deserialization error: {e}")
        except ConsumeError as e:
            self._logger.error(f"Kafka polling error during message consumption: {e}")
        except Exception as e:
            self._logger.error(f"Unknown error during message consumption: {e}")

    def subscribe_to_topics(self, topics: list[str]) -> bool:
        """
        Subscribes to the provided list of topics.

        :param topics: List of topics to subscribe to.
        :return: True if subscription was successful, False otherwise.
        """
        if self._consumer is None:
            self._logger.error("Consumer is not connected to Kafka.")
            return

        try:
            self._logger.info(f"Subscribing to topics: {topics}")
            self._consumer.subscribe(topics)
            return True
        except Exception as e:
            self._logger.error(f"Error during subscription to topics: {e}")
            return False

    def consume_loop(self, topics: list[str]):
        """
        Consumes messages from the Kafka topic in which the consumer is subscribed.
        """
        if self._consumer is None:
            self._logger.error("Consumer is not connected to Kafka.")
            return

        if not self.subscribe_to_topics(topics):
            self._logger.error("Failed to subscribe to topics.")
            return

        try:
            self._logger.info(f"Consuming from topics: {topics}")
            while True:
                self._polling_process()
        except KeyboardInterrupt:
            self._logger.info(f"Consumer stopped by user.")
        finally:
            self._consumer.close()
