import config
from src.producer import Producer
from src.repository import Repository
from src.simulator import Simulator, SimulatorConfig

repository = Repository(data_path=config.DATA_PATH)
producer = Producer(
    bootstrap_servers=config.KAFKA_BROKERS,
    topic=config.KAFKA_TOPIC
)
config = SimulatorConfig(
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
simulator = Simulator(
    repository=repository,
    producer=producer,
    config=config
)

if __name__ == "__main__":
    simulator.run()
