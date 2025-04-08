from trade_simulator.agents.basic_agent import BasicAgent
from trade_simulator.order.order import Order
import random


class SinglePoolFoolishRandomTrader(BasicAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO - check input parameters

        self.trader_type = "SinglePoolFoolishRandomTrader"
        self.parse_portfolio(kwargs["portfolio"])
        self.steps_to_make_new_transaction = kwargs["steps_to_make_new_transaction"]
        self.last_action_timestamp = 0
        self.pool_id = [kwargs["pool_id"]]
        self.probability_to_make_order = kwargs["probability_to_make_order"]

    def run_agent_action(self, timestamp: int):
        if timestamp - self.last_action_timestamp >= self.steps_to_make_new_transaction:
            self.make_order(timestamp)

    def parse_portfolio(self, input_portfolio):
        self.portfolio = {}
        for el in input_portfolio:
            self.portfolio[el["name"]] = el["quantity"]

    def make_order_decision(self) -> bool:
        return random.random() < self.probability_to_make_order

    def make_order(self, timestamp: int):
        if not self.make_order_decision():
            return
        self.last_action_timestamp = timestamp
        operation_type = random.choice("BUY", "SELL")
        token = random.choice(list(self.portfolio.keys()))
        order = Order(
            trader=self,
            creation_timestamp=timestamp,
            operation_type=operation_type,
            token=token,
            priority=1, # lowest priority
            # TODO - continue here
        )
