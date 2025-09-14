import sys

import config
from shared.logger import get_logger
from src.consumer import Consumer
from src.message_handler import MessageHandler
from src.worker.scheduler import Scheduler

logger = get_logger(component='main')

if __name__ == '__main__':
    with Scheduler(workers_count=config.WORKER_PROCESS_NUMBER) as scheduler:
        consumer = Consumer(
            bootstrap_servers=config.KAFKA_BROKERS,
            group_id=config.KAFKA_GROUP_ID,
            message_handler=MessageHandler(scheduler=scheduler)
        )

        if not consumer.connect_to_kafka():
            logger.error("Failed to connect to Kafka.")
            sys.exit(1)
        consumer.consume_loop(topics=[config.KAFKA_EVENT_TOPIC])
