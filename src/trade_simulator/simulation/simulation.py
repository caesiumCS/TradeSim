import os
from typing import Any, Dict

from trade_simulator.pool.pool import Pool
from trade_simulator.utils.utils import check_pools_settings


class Simulation:
    def __init__(self, **kwargs):
        self.simulation_build_args = kwargs["simulation"]
        self.simulation_meta_args = kwargs["meta_info"]

        self.prepare_experiment_environment()
        self.create_pools()

    def create_pools(self, pools_settings: Dict[str, Any]):
        pool_settings = self.simulation_build_args["pools_settings"]
        check_pools_settings(pools_settings)
        pools = {}
        for pool_settings in pools_settings["pools"]:
            pools[pool_settings["id"]] = Pool(**pool_settings)
        self.pools = pools

    def create_agents(self, agents_settings: Dict[str, Any]):
        pass

    def prepare_experiment_environment(self):
        experiment_id = self.simulation_meta_args["experiment_id"]
        experiment_name = self.simulation_meta_args["experiment_name"]
        experiment_name = "_".join(experiment_name.split())

        if not os.path.exists("Experiments_logs"):
            os.makedirs("Experiments_logs")

        if not os.path.exists(f"Experiments_logs/{experiment_name}"):
            os.makedirs(f"Experiments_logs/{experiment_name}")

        self.experiment_logs_path = f"Experiments_logs/{experiment_name}/Experiment_{experiment_id}"
        if not os.path.exists(self.experiment_logs_path ):
            os.makedirs(self.experiment_logs_path )
        else:
            raise ValueError(f"Experiment with name {experiment_name} and id {experiment_id} already exists.")

    def generate_metrics_by_pool(self, pool: Pool):
        pass
