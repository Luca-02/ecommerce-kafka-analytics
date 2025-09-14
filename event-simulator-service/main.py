import signal
from multiprocessing import Process

from shared.logger import get_logger

import config
from src.producer import Producer
from src.repository import MockRepository
from src.simulator import Simulator, SimulatorConfig

logger = get_logger(component='main')


def run_simulator(process_id: int):
    """
    Run a single simulator instance.

    :param process_id: ID of the process.
    """
    logger.info(f"Starting simulator process {process_id}...")
    simulator = Simulator(
        process_id=process_id,
        event_topic=config.KAFKA_EVENT_TOPIC,
        repository=MockRepository(data_path=config.DATA_PATH),
        producer=Producer(
            process_id=process_id,
            bootstrap_servers=config.KAFKA_BROKERS,
        ),
        config=SimulatorConfig(
            add_to_cart_probability=config.ADD_TO_CART_PROBABILITY,
            remove_from_cart_probability=config.REMOVE_FROM_CART_PROBABILITY,
            discount_probability=config.DISCOUNT_PROBABILITY,
            purchase_probability=config.PURCHASE_PROBABILITY,
            cart_quantity_range=(config.MIN_CART_QUANTITY, config.MAX_CART_QUANTITY),
            shipping_cost_range=(config.MIN_SHIPPING_COST, config.MAX_SHIPPING_COST),
            delivery_days_range=(config.MIN_DELIVERY_DAYS, config.MAX_DELIVERY_DAYS),
            session_interval_seconds_range=(config.MIN_SESSION_INTERVAL_SECONDS, config.MAX_SESSION_INTERVAL_SECONDS),
            event_interval_seconds_range=(config.MIN_EVENT_INTERVAL_SECONDS, config.MAX_EVENT_INTERVAL_SECONDS)
        )
    )
    simulator.run()


def stop_processes(processes_list: list[Process]):
    """
    Stop all running processes cleanly.

    :param processes_list: List of processes to stop.
    """
    logger.info("Stopping all processes...")
    for process in processes_list:
        if process.is_alive():
            process.terminate()
            process.join()
    logger.info("All processes stopped.")


if __name__ == "__main__":
    num_processes = config.NUMBER_SIMULATION_PROCESSES
    processes = []
    for i in range(num_processes):
        p = Process(target=run_simulator, args=(i,))
        p.start()
        processes.append(p)

    signal.signal(signal.SIGINT, lambda sig, frame: stop_processes(processes))
    signal.signal(signal.SIGTERM, lambda sig, frame: stop_processes(processes))
