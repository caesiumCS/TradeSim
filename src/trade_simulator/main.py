from trade_simulator.simulation.simulation import Simulation
from trade_simulator.utils.utils import read_settings

if __name__ == "__main__":
    print("Simulation started.")

    settings = read_settings("simulation.yaml")
    simulation = Simulation(**settings)
    simulation.run()
