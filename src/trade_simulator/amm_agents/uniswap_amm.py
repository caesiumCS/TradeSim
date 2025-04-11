from typing import TYPE_CHECKING
import random

from trade_simulator.amm_agents.basic_amm import AMM

if TYPE_CHECKING:
    from trade_simulator.order.order import Order
    from trade_simulator.pool.pool import Pool


class UniswapAMM(AMM):
    def __init__(self, pool: "Pool", **kwargs):
        super().__init__(pool, **kwargs)

        tokens = list(self.pool.tokens_info.keys())
        self.k = self.pool.tokens_info[tokens[0]] * self.pool.tokens_info[tokens[1]]

    def execute_order(self, order: "Order"):
        if order.status != "Awaiting":
            return

        if order.operation_type == "BUY":
            token_to_buy = order.token
            other_token = None
            for token in self.pool.tokens_info.keys():
                if token_to_buy != token:
                    other_token = token

            tokens_to_sell = (
                self.k / (self.pool.tokens_info[token_to_buy] - order.token_volume)
            ) - self.pool.tokens_info[other_token]

            if order.trader.portfolio[other_token] < tokens_to_sell:
                order.status = "Canceled"
                return
            order.trader.portfolio[other_token] -= tokens_to_sell
            self.pool.tokens_info[other_token] += tokens_to_sell
            order.trader.portfolio[token_to_buy] += order.token_volume
            self.pool.tokens_info[token_to_buy] -= order.token_volume
            order.status = "Succeed"

        else:
            token_to_sell = order.token
            other_token = None
            for token in self.pool.tokens_info.keys():
                if token_to_sell != token:
                    other_token = token

            tokens_to_buy = self.pool.tokens_info[other_token] - (
                self.k / (self.pool.tokens_info[token_to_buy] + order.token_volume)
            )

            if order.trader.portfolio[token_to_sell] < order.token_volume:
                order.status = "Canceled"
                return
            order.trader.portfolio[other_token] += tokens_to_buy
            self.pool.tokens_info[other_token] -= tokens_to_buy
            order.trader.portfolio[token_to_sell] -= order.token_volume
            self.pool.tokens_info[token_to_sell] += order.token_volume
            order.status = "Succeed"

    def sort_orders(self):
        random.shuffle(self.pool.order_book)
        self.pool.order_book = sorted(
            self.pool.order_book, key=lambda o: (o.creation_timestamp, o.priority)
        )
