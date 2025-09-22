import config
from shared.logger import get_logger
from src.consumer import Consumer
from src.event_processor import get_event_handlers_map
from src.message_handler import MessageHandler
from src.repository import FirebaseRepository
from src.worker.scheduler import Scheduler

logger = get_logger(component='main')

if __name__ == '__main__':
    with Scheduler(
        workers_count=config.WORKER_PROCESS_NUMBER
    ) as scheduler, \
        FirebaseRepository(
            google_application_credentials=config.GOOGLE_APPLICATION_CREDENTIALS
        ) as repository, \
        Consumer(
            message_handler=MessageHandler(
                scheduler=scheduler,
                event_handlers_map=get_event_handlers_map(repository)
            ),
            bootstrap_servers=config.KAFKA_BROKERS,
            group_id=config.KAFKA_GROUP_ID,
            ssl_ca_location=config.KAFKA_SSL_CA_LOCATION,
            ssl_check_hostname=config.KAFKA_SSL_CHECK_HOSTNAME,
            sasl_username=config.KAFKA_SASL_USERNAME,
            sasl_password=config.KAFKA_SASL_PASSWORD
        ) as consumer:
        consumer.consume_loop(topics=[config.KAFKA_EVENT_TOPIC])
