import sys
import time

from kafka import KafkaConsumer
from kafka.errors import KafkaError

from .message_handler import MessageHandler
from .logger_utils import get_logger

CONNECTION_MAX_ATTEMPTS = 10
CONNECTION_RETRY_DELAY_SECONDS = 5

lambda_decoder = lambda x: x.decode('utf-8') if x else None


class Consumer:
    def __init__(
        self,
        bootstrap_servers: str,
        group_id: str,
        topic: str,
        message_handler: MessageHandler
    ):
        self.consumer: KafkaConsumer | None = None
        self.logger = get_logger(component=f'consumer')
        self.consuming = False
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.topic = topic
        self.message_handler = message_handler
        self.consumer_config = {
            'client_id': 'analytics-service',
            'group_id': self.group_id,
            'bootstrap_servers': self.bootstrap_servers,
            'key_deserializer': lambda_decoder,
            'value_deserializer': lambda_decoder,
            'auto_offset_reset': 'earliest',
            'enable_auto_commit': False,
            'max_poll_records': 100,
            'session_timeout_ms': 30000,
            'heartbeat_interval_ms': 3000
        }

    def _process_records(self, records: dict):
        """
        Processes the records received from Kafka.
        """
        if not records:
            return

        for topic_partition, messages in records.items():
            self.logger.info(f"Processing {len(messages)} messages "
                             f"from topic {topic_partition.topic} "
                             f"in partition {topic_partition.partition}")
            for message in messages:
                self.message_handler.handle(message)
            self.consumer.commit()
            self.logger.info("Offset committed successfully.")

    def connect_and_subscribe_to_kafka(self):
        """
        Connects to Kafka and subscribes to the topic.
        """
        if self.consumer:
            self.logger.info("Already connected to Kafka.")
            return

        self.logger.info("Connecting to Kafka...")
        for attempt in range(CONNECTION_MAX_ATTEMPTS):
            try:
                self.consumer = KafkaConsumer(self.topic, **self.consumer_config)
                self.logger.info(f"Connected to Kafka through: {self.bootstrap_servers}")
                self.logger.info(f"Subscribed to topics: {self.topic}")
                return
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < CONNECTION_MAX_ATTEMPTS - 1:
                    self.logger.info(f"Retrying in {CONNECTION_RETRY_DELAY_SECONDS} seconds...")
                    time.sleep(CONNECTION_RETRY_DELAY_SECONDS)
                else:
                    self.logger.error(f"Impossible to connect to Kafka after {CONNECTION_MAX_ATTEMPTS} attempts.")
                    sys.exit(1)

    def consume_from_topics(self):
        """
        Consumes messages from the Kafka topic in which the consumer is subscribed.
        """
        if self.consumer is None:
            self.logger.error("Consumer is not connected to Kafka.")
            return

        self.logger.info(f"Consuming from topics: {self.topic}")
        self.consuming = True
        try:
            while self.consuming:
                try:
                    records = self.consumer.poll(timeout_ms=1000)
                    self._process_records(records)
                except KafkaError as e:
                    self.logger.error(f"Kafka error during consumption: {e}")
                except Exception as e:
                    self.logger.error(f"Unknown error during consumption: {e}")
        except KeyboardInterrupt:
            self.logger.info(f"Consumer stopped by user.")
        finally:
            self.logger.info("Finishing consumption...")
            self.close()
            self.logger.info("Consumer finished.")

    def close(self):
        """
        Closes the consumer stopping the consumption process.
        """
        self.logger.info("Closing consumer...")
        if self.consumer:
            try:
                self.consuming = False
                self.consumer.close()
                self.logger.info("Consumer closed cleanly!")
            except Exception as e:
                self.logger.error(f"Error during consumer close: {e}")
