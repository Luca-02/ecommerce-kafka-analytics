from simulator import Simulator

simulator = Simulator()

if __name__ == "__main__":
    events = simulator.simulate_user_session()

    for event in events:
        print(event)
