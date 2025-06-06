from typing import Any, Dict, List, Union

from trade_simulator.amm_agents.basic_amm import AMM
from trade_simulator.amm_agents.uniswap_amm import UniswapAMM
from trade_simulator.order.order import Order
from trade_simulator.utils.consts import ORDER_OPERATION_STATUSES


class Pool:
    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.name = kwargs["name"]
        self.steps_to_check_orderbook = kwargs["steps_to_check_orderbook"]
        self.last_timestamp_to_check_orderbook = kwargs["step_to_start_simulation"]

        self.tokens_info = self.create_tokens_pool(kwargs["tokens"])
        self.order_book: List[Order] = []

        self.metrics = {
            "total_number_of_unique_orders": 0,
            "number_of_orders_in_order_book": [],
            "portfolio": {},
        }
        self.amm_agent = self.generate_amm(kwargs["amm_settings"])

        for token in self.tokens_info.keys():
            self.metrics["portfolio"][token] = []

        for status in ORDER_OPERATION_STATUSES:
            self.metrics[f"number_of_{status}_orders_in_order_book"] = []

    def generate_amm(self, amm_settings: Dict[str, Any]) -> AMM:
        if amm_settings["type"] == "Uniswap":
            return UniswapAMM(self, **amm_settings)
        elif amm_settings["type"] == "Mariana":
            return None

    def create_tokens_pool(
        self, tokens_info: Dict[str, Union[str, int]]
    ) -> Dict[str, int]:
        token_to_quantity = {}
        for token_info in tokens_info:
            token_to_quantity[token_info["name"]] = token_info["start_quantity"]
        return token_to_quantity

    def execute_orders(self, timestamp: int):
        if (
            self.last_timestamp_to_check_orderbook + self.steps_to_check_orderbook
            >= timestamp
        ):
            self.amm_agent.execute_orders(timestamp)
            self.last_timestamp_to_check_orderbook = timestamp
        self.amm_agent.clean_order_book()
        for token in self.tokens_info.keys():
            self.metrics["portfolio"][token].append(self.tokens_info[token])

    def add_order(self, order: Order):
        self.order_book.append(order)
        self.metrics["total_number_of_unique_orders"] += 1
