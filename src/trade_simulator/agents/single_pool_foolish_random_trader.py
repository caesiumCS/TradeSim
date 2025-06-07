import random

from trade_simulator.agents.basic_agent import BasicAgent
from trade_simulator.order.order import Order


class SinglePoolFoolishRandomTrader(BasicAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO - check input parameters

        self.type = "SinglePoolFoolishRandomTrader"
        self.steps_to_make_new_transaction = kwargs["steps_to_make_new_transaction"]
        self.last_action_timestamp = 0
        self.pool_id = [kwargs["pool_id"]]
        self.probability_to_make_order = kwargs["probability_to_make_order"]
        self.pool = None
        self.metrics["pool_id"] = self.pool_id
        self.token_as_currency = kwargs["token_as_currency"]

    def run_agent_action(self, timestamp: int):
        if timestamp - self.last_action_timestamp >= self.steps_to_make_new_transaction:
            self.make_order(timestamp)

    def make_order_decision(self) -> bool:
        return random.random() < self.probability_to_make_order

    def get_token(self) -> str:
        return random.choice(list(self.portfolio.keys()))

    def get_other_token(self, current_token: str):
        tokens = list(self.portfolio.keys())
        tokens.remove(current_token)
        return random.choice(tokens)

    def get_order_volume(self, token: str, operation_type: str) -> int:
        return random.choice([1, 2, 3])

    def make_order(self, timestamp: int):
        if not self.make_order_decision():
            return
        operation_type = random.choice(["BUY", "SELL"])
        token = self.get_token()
        token_volume = self.get_order_volume(token, operation_type)
        order = Order(
            trader=self,
            creation_timestamp=timestamp,
            operation_type=operation_type,
            token=token,
            token_volume=token_volume,
            priority=1,
            second_token=self.get_other_token(token)
        )
        self.last_action_timestamp = timestamp
        self.pool.add_order(order)

    def update_metrics(self):
        for token in self.portfolio.keys():
            self.metrics["portfolio"][token].append(self.portfolio[token])

        if self.pool.amm_agent.type == "UniswapV2":
            other_token = self.pool.amm_agent._get_other_token(self.token_as_currency)
            current_asset_price_in_currency = (
                self.pool.amm_agent.get_asset_price_in_currency(
                    other_token,
                    self.token_as_currency,
                    self.portfolio[other_token],
                )
            )
            self.metrics["budget_in_currency"].append(
                current_asset_price_in_currency * self.portfolio[other_token]
            )
        elif self.pool.amm_agent.type == "Mariana":
            other_tokens = self.pool.amm_agent._get_other_token(self.token_as_currency)
            total_sum = 0
            for token in other_tokens:
                current_asset_price_in_currency = (
                    self.pool.amm_agent.get_asset_price_in_currency(
                        token,
                        self.token_as_currency,
                        self.portfolio[token],
                    )
                )
                total_sum += current_asset_price_in_currency * self.portfolio[token]
            self.metrics["budget_in_currency"].append(total_sum)
