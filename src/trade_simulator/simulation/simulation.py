import json
import os
import random
import shutil

from tqdm import tqdm

from trade_simulator.agents.simple_market_maker import SimpleMarketMaker
from trade_simulator.agents.single_pool_foolish_random_trader import (
    SinglePoolFoolishRandomTrader,
)
from trade_simulator.pool.pool import Pool
from trade_simulator.utils.plots import (
    plot_agent_balance,
    plot_pair_balance,
    plot_pool_balace,
    plot_k,
    plot_profit_from_fees,
    plot_agent_orders,
)
from trade_simulator.utils.utils import check_pools_settings


class Simulation:
    def __init__(self, **kwargs):
        self.simulation_build_args = kwargs["simulation"]
        self.steps = self.simulation_build_args["steps_of_simulation"]
        self.simulation_meta_args = kwargs["meta_info"]

        self.prepare_experiment_environment()
        self.create_pools()
        self.create_agents()

    def run(self):
        for step in tqdm(range(self.steps)):
            for pool_id in self.pools.keys():
                self.pools[pool_id].execute_orders(step)
            random.shuffle(self.agents)
            for agent in self.agents:
                agent.complete_agent_action(step)
            for pool in self.pools.values():
                pool.amm_agent.write_metrics()
        self.save_metrics_after_simulation()

    def save_metrics_after_simulation(self):
        self.save_raw_pools_data()
        self.save_raw_agents_data()
        for pool in self.pools.values():
            self.generate_metrics_by_pool(pool)
        path = f"{self.experiment_logs_path}/agents_metrics"
        if not os.path.exists(path):
            os.makedirs(path)
        print("Generating metrics by agents...")
        for agent in tqdm(self.agents):
            self.generate_metrics_by_agent(agent)

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
        if "agents" in agents_settings:
            for agent in agents_settings["agents"]:
                agent_type = agent["agent_type"]
                agent_settings = agent["agent_settings"]
                agent = self.generate_agent(agent_type, agent_settings)
                self.agents.append(agent)
        self.put_ids_to_agents()

    def generate_agent(self, agent_type, agent_settings):
        agent = None
        if agent_type == "SinglePoolFoolishRandomTrader":
            agent = SinglePoolFoolishRandomTrader(**agent_settings)
            agent.pools = {
                agent_settings["pool_id"]: self.pools[agent_settings["pool_id"]]
            }
            agent.pool = self.pools[agent_settings["pool_id"]]
        elif agent_type == "SimpleMarketMaker":
            agent = SimpleMarketMaker(**agent_settings)
            for rule in agent.rules:
                agent.pools[rule["pool_id"]] = self.pools[rule["pool_id"]]
        else:
            raise ValueError(f"Unknown agent type {agent_type}.")
        return agent

    def generate_agents_batch(self, agents_batche_settings):
        agent_type = agents_batche_settings["agent_type"]
        agent_settings = agents_batche_settings["agent_settings"]
        for _ in range(agents_batche_settings["number_of_agents"]):
            agent = self.generate_agent(agent_type, agent_settings)
            self.agents.append(agent)

    def put_ids_to_agents(self):
        for i, agent in enumerate(self.agents):
            agent.id = i
            agent.metrics["id"] = i
            agent.metrics["type"] = agent.type

    def prepare_experiment_environment(self, delete_existing_folder: bool = True):
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
            if not delete_existing_folder:
                raise ValueError(
                    f"Experiment with name {experiment_name} and id {experiment_id} already exists."
                )
            for item in os.listdir(self.experiment_logs_path):
                item_path = os.path.join(self.experiment_logs_path, item)
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

    def save_raw_pools_data(self):
        print("Saving raw pools data...")
        path = f"{self.experiment_logs_path}/raw_pools_data"
        if not os.path.exists(path):
            os.makedirs(path)
        for pool_id, pool in self.pools.items():
            with open(f"{path}/pool_{pool_id}.json", "w") as f:
                json.dump(pool.metrics, f)

    def save_raw_agents_data(self):
        print("Saving raw agents data...")
        path = f"{self.experiment_logs_path}/raw_agents_data"
        if not os.path.exists(path):
            os.makedirs(path)
        for agent in tqdm(self.agents):
            with open(f"{path}/{agent.type}_{agent.id}.json", "w") as f:
                json.dump(agent.metrics, f)

    def generate_metrics_by_pool(self, pool: Pool):
        path = f"{self.experiment_logs_path}/pool_{pool.id}_metrics"
        if not os.path.exists(path):
            os.makedirs(path)
        plot_pool_balace(pool, path)
        plot_k(pool, path)
        if pool.amm_agent.type == "UniswapV2":
            plot_pair_balance(pool, path)
        if "profit_from_fees" in pool.metrics:
            plot_profit_from_fees(pool, path)

    def generate_metrics_by_agent(self, agent):
        path = f"{self.experiment_logs_path}/agents_metrics/{agent.type}_{agent.id}_metrics"
        if not os.path.exists(path):
            os.makedirs(path)
        plot_agent_balance(agent, path)
        plot_agent_orders(agent, path)
