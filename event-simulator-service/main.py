from concurrent.futures import ProcessPoolExecutor

import config
from shared.logger import get_logger
from src.data_generation import generate_data
from src.producer import Producer
from src.repository import Repository
from src.simulator import Simulator, SimulatorConfig

logger = get_logger(component='main')


def run_simulator(process_id: int):
    """
    Run a single simulator instance.

    :param process_id: ID of the process.
    """
    logger.info(f"Starting simulator process {process_id}...")
    with Producer(
        process_id=process_id,
        bootstrap_servers=config.KAFKA_BROKERS,
        ssl_ca_location=config.KAFKA_SSL_CA_LOCATION,
        ssl_check_hostname=config.KAFKA_SSL_CHECK_HOSTNAME,
        sasl_username=config.KAFKA_SASL_USERNAME,
        sasl_password=config.KAFKA_SASL_PASSWORD
    ) as producer:
        Simulator(
            process_id=process_id,
            event_topic=config.KAFKA_EVENT_TOPIC,
            repository=Repository(data_path=config.DATA_PATH),
            producer=producer,
            config=SimulatorConfig(
                add_to_cart_probability=config.ADD_TO_CART_PROBABILITY,
                remove_from_cart_probability=config.REMOVE_FROM_CART_PROBABILITY,
                discount_probability=config.DISCOUNT_PROBABILITY,
                purchase_probability=config.PURCHASE_PROBABILITY,
                cart_quantity_range=(config.MIN_CART_QUANTITY, config.MAX_CART_QUANTITY),
                shipping_cost_range=(config.MIN_SHIPPING_COST, config.MAX_SHIPPING_COST),
                delivery_days_range=(config.MIN_DELIVERY_DAYS, config.MAX_DELIVERY_DAYS),
                session_interval_seconds_range=(
                    config.MIN_SESSION_INTERVAL_SECONDS, config.MAX_SESSION_INTERVAL_SECONDS),
                event_interval_seconds_range=(config.MIN_EVENT_INTERVAL_SECONDS, config.MAX_EVENT_INTERVAL_SECONDS)
            )
        ).run()


if __name__ == "__main__":
    generate_data()
    try:
        with ProcessPoolExecutor(max_workers=config.NUMBER_SIMULATION_PROCESSES) as executor:
            futures = [
                executor.submit(run_simulator, i)
                for i in range(config.NUMBER_SIMULATION_PROCESSES)
            ]
    except KeyboardInterrupt:
        logger.info("Simulation interrupted.")
