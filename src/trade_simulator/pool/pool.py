from typing import Any, Dict, List, Union

from trade_simulator.amm_agents.basic_amm import AMM
from trade_simulator.amm_agents.uniswap_amm import UniswapAMM
from trade_simulator.order.order import Order


class Pool:
    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.name = kwargs["name"]

        self.tokens_info = self.create_tokens_pool(kwargs["tokens"])
        self.amm_agent = self.generate_amm(kwargs["amm_settings"])

        self.order_book: List[Order] = []

    def generate_amm(self, amm_settings: Dict[str, Any]) -> AMM:
        if amm_settings["type"] == "Uniswap":
            return UniswapAMM(self, amm_settings)

    def create_tokens_pool(
        self, tokens_info: Dict[str, Union[str, int]]
    ) -> Dict[str, int]:
        token_to_quantity = {}
        for token_info in tokens_info:
            token_to_quantity[token_info["name"]] = token_info["start_quantity"]
        return token_to_quantity

    def execute_orders(self):
        self.amm_agent.execute_orders()
