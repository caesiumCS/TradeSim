from typing import Any, Dict, List, Union

from trade_simulator.amm_agents.basic_amm import AMM
from trade_simulator.amm_agents.uniswap_amm import UniswapAMM
from trade_simulator.order.order import Order


class Pool:
    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.name = kwargs["name"]
        self.steps_to_check_orderbook = kwargs["steps_to_check_orderbook"]
        self.last_timestamp_to_check_orderbook = kwargs["step_to_start_simulation"]

        self.tokens_info = self.create_tokens_pool(kwargs["tokens"])
        self.amm_agent = self.generate_amm(kwargs["amm_settings"])

        self.order_book: List[Order] = []

        self.metrics = {
            "total_number_of_orders": [],
        }

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

    def execute_orders(self, timestamp:int):
        if self.last_timestamp_to_check_orderbook + self.steps_to_check_orderbook >= timestamp:
            self.amm_agent.execute_orders()
            self.last_timestamp_to_check_orderbook = timestamp

    def add_order(self, order: Order):
        self.order_book.append(order)
        self.metrics["total_number_of_orders"] += 1
