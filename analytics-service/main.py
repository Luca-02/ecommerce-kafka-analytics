import config

from src.logger_utils import get_logger
from src.consumer import Consumer
from src.message_handler import MessageHandler

logger = get_logger(component='main')

if __name__ == '__main__':
    consumer = Consumer(
        bootstrap_servers=config.KAFKA_BROKERS,
        group_id=config.KAFKA_GROUP_ID,
        topic=config.KAFKA_EVENT_TOPIC,
        message_handler=MessageHandler()
    )
    consumer.connect_and_subscribe_to_kafka()
    consumer.consume_from_topics()
