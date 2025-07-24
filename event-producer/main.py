from config import DATA_PATH
from src.producer import Producer
from src.repository import Repository
from src.simulator import Simulator

repository = Repository(DATA_PATH)
producer = Producer()
simulator = Simulator(repository, producer)

if __name__ == "__main__":
    simulator.run()
