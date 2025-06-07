from typing import TYPE_CHECKING

from trade_simulator.amm_agents.uniswap_amm import UniswapAMM

if TYPE_CHECKING:
    from trade_simulator.order.order import Order
    from trade_simulator.pool.pool import Pool

class MarianaAMM(UniswapAMM):

    def __init__(self, pool: "Pool", **kwargs):
        self.pool = pool
        self.settings = kwargs
        self.type = None
        self.fee = 0.0 if "fee" not in self.settings else self.settings["fee"]

        self.type = "Mariana"
        self.tokens = list(self.pool.tokens_info.keys())
        self.pool.metrics["k"] = []
        self.pool.metrics["profit_from_fees"] = {}
        for token in self.tokens:
            self.pool.metrics["profit_from_fees"][token] = {"timestamp": [0], "value": [0]}

    def write_metrics(self):
        k_value = 1
        for token in self.tokens:
            k_value *= self.pool.tokens_info[token]
        self.pool.metrics["k"].append(k_value)
