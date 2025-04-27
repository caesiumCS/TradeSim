import math
import random
from typing import TYPE_CHECKING

from trade_simulator.amm_agents.basic_amm import AMM

if TYPE_CHECKING:
    from trade_simulator.order.order import Order
    from trade_simulator.pool.pool import Pool


class MarianaAMM(AMM):
    def __init__(
        self,
        pool: "Pool",
        weights: dict[str, float] = None,
        fee_rate: float = 0.0005,
        **kwargs,
    ):
        """
        pool.tokens_info: {'EUR': amt, 'SGD': amt, 'CHF': amt}
        weights: dict of token weights summing to 1, default equal.
        fee_rate: комиссия на входящие объёмы.
        """
        super().__init__(pool, **kwargs)
        symbols = list(pool.tokens_info.keys())
        if weights is None:
            w = 1.0 / len(symbols)
            self.weights = {t: w for t in symbols}
        else:
            self.weights = weights
        self.fee_rate = fee_rate
        self.k = self._compute_invariant(pool.tokens_info)

    def _compute_invariant(self, reserves: dict[str, float]) -> float:
        k = 1.0
        for token, R in reserves.items():
            k *= R ** self.weights[token]
        return k

    def execute_order(self, order: "Order"):
        if order.status != "Awaiting":
            return

        R = self.pool.tokens_info
        # BUY: трейдер хочет получить `want`, отдавая один из других токенов или оба
        if order.operation_type == "BUY":
            want = order.token
            gives = [t for t in R if t != want]

            best = None  # (give, amount_in_with_fee, amount_in, fee)
            for give in gives:
                # Рассчитываем объём входа для каждого варианта
                fixed_prod = 1.0
                for t in R:
                    if t != want:
                        fixed_prod *= R[t] ** self.weights[t]
                R_want_target = R[want] - order.token_volume
                if R_want_target <= 0:
                    continue
                prod_others = 1.0
                for t in R:
                    if t not in (want, give):
                        prod_others *= R[t] ** self.weights[t]
                numerator = self.k / (
                    (R_want_target ** self.weights[want]) * prod_others
                )
                R_give_new = numerator ** (1.0 / self.weights[give])
                amount_in = R_give_new - R[give]
                fee = amount_in * self.fee_rate
                amount_in_with_fee = amount_in
                total_in = amount_in + fee
                if best is None or amount_in_with_fee < best[1]:
                    # best = (give, amount_in_with_fee, amount_in, fee)
                    best = (give, total_in, amount_in, fee)

            if best is None:
                order.status = "Canceled"
                return

            give, amount_in_with_fee, amount_in, fee = best
            if order.trader.portfolio[give] < amount_in_with_fee:
                order.status = "Canceled"
                return

            # order.trader.portfolio[give] -= amount_in_with_fee
            # self.pool.tokens_info[give] += amount_in
            order.trader.portfolio[give] -= total_in
            self.pool.tokens_info[give] += total_in
            order.trader.portfolio[want] += order.token_volume
            self.pool.tokens_info[want] -= order.token_volume

        else:  # SELL: трейдер продаёт `sell`, получает один из других токенов
            sell = order.token
            buys = [t for t in R if t != sell]

            best = None  # (buy, amount_out)
            for buy in buys:
                amount_in = order.token_volume
                fee = amount_in * self.fee_rate
                net_in = amount_in - fee
                R_sell_new = R[sell] + net_in
                prod_others = 1.0
                for t in R:
                    if t not in (sell, buy):
                        prod_others *= R[t] ** self.weights[t]
                fixed = prod_others * (R_sell_new ** self.weights[sell])
                R_buy_new = (self.k / fixed) ** (1.0 / self.weights[buy])
                amount_out = R[buy] - R_buy_new
                if amount_out <= 0:
                    continue
                if best is None or amount_out > best[1]:
                    best = (buy, amount_out, net_in, fee)

            if best is None:
                order.status = "Canceled"
                return

            buy, amount_out, net_in, fee = best
            if order.trader.portfolio[sell] < order.token_volume:
                order.status = "Canceled"
                return

            order.trader.portfolio[sell] -= order.token_volume
            self.pool.tokens_info[sell] += net_in
            order.trader.portfolio[buy] += amount_out
            self.pool.tokens_info[buy] -= amount_out

        order.status = "Succeed"
        # Пересчитываем инвариант после сделки
        self.k = self._compute_invariant(self.pool.tokens_info)

    def sort_orders(self):
        random.shuffle(self.pool.order_book)
        self.pool.order_book = sorted(
            self.pool.order_book, key=lambda o: (o.creation_timestamp, o.priority)
        )
