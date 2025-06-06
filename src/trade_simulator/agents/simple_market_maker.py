import random

from trade_simulator.agents.basic_agent import BasicAgent
from trade_simulator.order.order import Order


class SimpleMarketMaker(BasicAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = "SimpleMarketMaker"
        self.pools = {}
        self.rules = kwargs["rules"]
        for rule in self.rules:
            rule["steps_without_action"] = 0
        self.metrics["budget_in_currency"] = []

    def is_make_action(self, pool, rule, timestamp: int):
        if (
            rule["steps_without_action"]
            >= rule["steps_to_make_action_in_case_passivity"]
        ):
            return True
        current_asset_price_in_currency = pool.amm_agent.get_asset_price_in_currency(
            rule["token_as_asset"],
            rule["token_as_currency"],
        )
        if (
            current_asset_price_in_currency
            < rule["lower_bound_of_asset_price_in_currency"]
            or current_asset_price_in_currency
            > rule["upper_bound_of_asset_price_in_currency"]
        ):
            return True
        return False

    def run_action_by_rule(self, rule, timestamp: int):
        pool = self.pools[rule["pool_id"]]
        token_as_asset = rule["token_as_asset"]
        token_as_currency = rule["token_as_currency"]
        lower_bound_of_asset_price_in_currency = rule[
            "lower_bound_of_asset_price_in_currency"
        ]
        upper_bound_of_asset_price_in_currency = rule[
            "upper_bound_of_asset_price_in_currency"
        ]
        if not self.is_make_action(pool, rule, timestamp):
            rule["steps_without_action"] += 1
            return

        current_asset_price_in_currency = pool.amm_agent.get_asset_price_in_currency(
            token_as_asset,
            token_as_currency,
        )

        # TODO - make a smarter logic for choosing volume
        if current_asset_price_in_currency < lower_bound_of_asset_price_in_currency:
            order = Order(
                trader=self,
                creation_timestamp=timestamp,
                operation_type="BUY",
                token=token_as_asset,
                token_volume=random.choice(list(range(1, 100))),
                priority=1,  # lowest priority
                second_token=token_as_currency,
            )
            pool.add_order(order)
        elif current_asset_price_in_currency > upper_bound_of_asset_price_in_currency:
            order = Order(
                trader=self,
                creation_timestamp=timestamp,
                operation_type="SELL",
                token=token_as_asset,
                token_volume=random.choice(list(range(1, 100))),
                priority=1,  # lowest priority
                second_token=token_as_currency,
            )
            pool.add_order(order)
        rule["steps_without_action"] = 0

    def run_agent_action(self, timestamp: int):
        for rule in self.rules:
            self.run_action_by_rule(rule, timestamp)

    def update_metrics(self):
        for token in self.portfolio.keys():
            self.metrics["portfolio"][token].append(self.portfolio[token])
        for rule in self.rules:
            pool = self.pools[rule["pool_id"]]
            current_asset_price_in_currency = (
                pool.amm_agent.get_asset_price_in_currency(
                    rule["token_as_asset"],
                    rule["token_as_currency"],
                    self.portfolio[rule["token_as_asset"]],
                )
            )
            self.metrics["budget_in_currency"].append(
                current_asset_price_in_currency * self.portfolio[rule["token_as_asset"]]
            )
