from config import DATA_PATH, KAFKA_BROKERS, KAFKA_TOPIC
from src.producer import Producer
from src.repository import Repository
from src.simulator import Simulator

repository = Repository(DATA_PATH)
producer = Producer(KAFKA_BROKERS, KAFKA_TOPIC)
simulator = Simulator(repository, producer)

if __name__ == "__main__":
    simulator.run()
