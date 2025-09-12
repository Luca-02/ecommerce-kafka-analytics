from confluent_kafka import DeserializingConsumer, KafkaError
from confluent_kafka.error import ConsumeError, KeyDeserializationError, ValueDeserializationError
from confluent_kafka.serialization import StringDeserializer

from .logger_utils import get_logger
from .message_handler import MessageHandler


class Consumer:
    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        message_handler: MessageHandler
    ):
        self.logger = get_logger(component=f'consumer')
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.message_handler = message_handler
        self.config = {
            "client.id": "analytics-service",
            "group.id": self.group_id,
            "bootstrap.servers": self.bootstrap_servers,
            "key.deserializer": StringDeserializer(),
            "value.deserializer": StringDeserializer(),
            "auto.offset.reset": "earliest",
            'on_commit': self._commit_completed
        }
        self.consumer: DeserializingConsumer | None = None
        self.poll_timeout_sec = 1.0

    def _commit_completed(self, err, _):
        if err:
            self.logger.error(f"Error during commit: {err}")
        else:
            self.logger.info(f"Committed partition offsets")

    def _polling_process(self):
        """
        Polls for messages from Kafka and processes them.
        """
        try:
            msg = self.consumer.poll(timeout=1.0)
            if msg is None:
                return

            if msg.error() and msg.error().code() != KafkaError._PARTITION_EOF:  # End of partition event
                self.logger.error(f"Error during message processing: {msg.error()}")
            else:
                # Process the message
                self.message_handler.handle(msg)
        except KeyDeserializationError as e:
            self.logger.error(f"Kafka message key deserialization error: {e}")
        except ValueDeserializationError as e:
            self.logger.error(f"Kafka message value deserialization error: {e}")
        except ConsumeError as e:
            self.logger.error(f"Kafka polling error during message consumption: {e}")
        except Exception as e:
            self.logger.error(f"Unknown error during message consumption: {e}")

    def connect_to_kafka(self) -> bool:
        """
        Connects to Kafka using the provided configuration.

        :return: True if connection was successful, False otherwise.
        """
        if self.consumer:
            self.logger.info("Already connected to Kafka.")
            return True

        try:
            self.consumer = DeserializingConsumer(self.config)
            self.logger.info(f"Connected to Kafka through: {self.bootstrap_servers}")
            return True
        except Exception as e:
            self.logger.error(f"Error during connection to Kafka: {e}")
            return False

    def subscribe_to_topics(self, topics: list[str]) -> bool:
        """
        Subscribes to the provided list of topics.

        :param topics: List of topics to subscribe to.
        :return: True if subscription was successful, False otherwise.
        """
        try:
            self.logger.info(f"Subscribing to topics: {topics}")
            self.consumer.subscribe(topics)
            return True
        except Exception as e:
            self.logger.error(f"Error during subscription to topics: {e}")
            return False

    def consume_loop(self, topics: list[str]):
        """
        Consumes messages from the Kafka topic in which the consumer is subscribed.
        """
        if self.consumer is None:
            self.logger.error("Consumer is not connected to Kafka.")
            return

        if not self.subscribe_to_topics(topics):
            self.logger.error("Failed to subscribe to topics.")
            return

        try:
            self.logger.info(f"Consuming from topics: {topics}")
            while True:
                self._polling_process()
        except KeyboardInterrupt:
            self.logger.info(f"Consumer stopped by user.")
        finally:
            self.consumer.close()

    def close(self):
        """
        Closes the consumer stopping the consumption process.
        """
        self.logger.info("Closing consumer...")
        if self.consumer:
            try:
                if self.consumer:
                    self.consumer.close()
                    self.consumer = None
                self.logger.info("Consumer closed cleanly!")
            except Exception as e:
                self.logger.error(f"Error during consumer close: {e}")
