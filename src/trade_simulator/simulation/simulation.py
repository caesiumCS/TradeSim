from typing import Any, Dict, List

from trade_simulator.pool.pool import Pool
from trade_simulator.utils.utils import check_pools_settings


class Simulation:
    def __init__(self, **kwargs):
        self.simulation_build_args = kwargs["simulation"]
        self.simulation_meta_args = kwargs["meta_info"]

        self.pools = self.create_pools(self.simulation_build_args["pools_settings"])


    def create_pools(self, pools_settings: Dict[str, Any]) -> List[Pool]:
        check_pools_settings(pools_settings)
        pools = []
        for pool_settings in pools_settings["pools"]:
            pools.append(Pool(**pool_settings))
        return pools



