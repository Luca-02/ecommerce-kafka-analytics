import sys

import config
from src.consumer import Consumer
from src.logger_utils import get_logger
from src.message_handler import MessageHandler

logger = get_logger(component='main')

if __name__ == '__main__':
    consumer = Consumer(
        bootstrap_servers=config.KAFKA_BROKERS,
        group_id=config.KAFKA_GROUP_ID,
        message_handler=MessageHandler()
    )
    if not consumer.connect_to_kafka():
        logger.error("Failed to connect to Kafka.")
        sys.exit(1)
    consumer.consume_loop(topics=[config.KAFKA_EVENT_TOPIC])
