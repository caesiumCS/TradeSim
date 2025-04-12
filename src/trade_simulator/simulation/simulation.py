import os
from tqdm import tqdm
import random
import json

from trade_simulator.agents.single_pool_foolish_random_trader import (
    SinglePoolFoolishRandomTrader,
)
from trade_simulator.pool.pool import Pool
from trade_simulator.utils.utils import check_pools_settings


class Simulation:
    def __init__(self, **kwargs):
        self.simulation_build_args = kwargs["simulation"]
        self.steps = self.simulation_build_args["steps_of_simulation"]
        self.simulation_meta_args = kwargs["meta_info"]

        # self.prepare_experiment_environment()
        self.create_pools()
        self.create_agents()


    def run(self):
        for step in tqdm(range(self.steps)):
            for pool_id in self.pools.keys():
                self.pools[pool_id].execute_orders(step)
            random.shuffle(self.agents)
            for agent in self.agents:
                agent.run_agent_action(step)

        with open('pool_3.json', 'w') as f:
            json.dump(self.pools[1].metrics, f)

    def create_pools(self):
        pools_settings = self.simulation_build_args["pools_settings"]
        check_pools_settings(pools_settings)
        pools = {}
        for pool_settings in pools_settings["pools"]:
            pools[pool_settings["id"]] = Pool(**pool_settings)
        self.pools = pools

    def create_agents(self):
        self.agents = []
        agents_settings = self.simulation_build_args["agents_settings"]
        if "agents_batches" in agents_settings:
            for batch in agents_settings["agents_batches"]:
                self.generate_agents_batch(batch)

    def generate_agents_batch(self, agents_batche_settings):
        agent_type = agents_batche_settings["agent_type"]
        agent_settings = agents_batche_settings["agent_settings"]
        for _ in range(agents_batche_settings["number_of_agents"]):
            agent = None
            if agent_type == "SinglePoolFoolishRandomTrader":
                agent = SinglePoolFoolishRandomTrader(**agent_settings)
                agent.pools = {
                    agent_settings["pool_id"]: self.pools[agent_settings["pool_id"]]
                }
                agent.pool = self.pools[agent_settings["pool_id"]]
            else:
                raise ValueError(f"Unknown agent type {agent_type}.")
            self.agents.append(agent)

    def prepare_experiment_environment(self):
        experiment_id = self.simulation_meta_args["experiment_id"]
        experiment_name = self.simulation_meta_args["experiment_name"]
        experiment_name = "_".join(experiment_name.split())

        if not os.path.exists("Experiments_logs"):
            os.makedirs("Experiments_logs")

        if not os.path.exists(f"Experiments_logs/{experiment_name}"):
            os.makedirs(f"Experiments_logs/{experiment_name}")

        self.experiment_logs_path = (
            f"Experiments_logs/{experiment_name}/Experiment_{experiment_id}"
        )
        if not os.path.exists(self.experiment_logs_path):
            os.makedirs(self.experiment_logs_path)
        else:
            raise ValueError(
                f"Experiment with name {experiment_name} and id {experiment_id} already exists."
            )

    def generate_metrics_by_pool(self, pool: Pool):
        pass
