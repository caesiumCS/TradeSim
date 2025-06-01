import random
from typing import TYPE_CHECKING

from trade_simulator.amm_agents.basic_amm import AMM

if TYPE_CHECKING:
    from trade_simulator.order.order import Order
    from trade_simulator.pool.pool import Pool


class UniswapAMM(AMM):
    def __init__(self, pool: "Pool", **kwargs):
        super().__init__(pool, **kwargs)

        tokens = list(self.pool.tokens_info.keys())
        self.type = "UniswapV2"
        self.token_a, self.token_b = tokens
        self.pool.metrics["k"] = []
        self.pool.metrics["k"].append(
            self.pool.tokens_info[self.token_a] * self.pool.tokens_info[self.token_b]
        )

    def write_metrics(self):
        self.pool.metrics["k"].append(
            self.pool.tokens_info[self.token_a] * self.pool.tokens_info[self.token_b]
        )

    def _get_other_token(self, token: str) -> str:
        """
        Возвращает другой токен в пуле, кроме указанного.
        UniswapV2 предполагает, что в пуле только два токена.
        :param token: Токен, для которого нужно найти другой токен.
        :return: Другой токен в пуле.
        """
        return self.token_b if token == self.token_a else self.token_a

    def _buy_market(self, order: "Order"):
        token_out = order.token  # токен, который трейдер хочет получить
        token_in = self._get_other_token(token_out)

        x = self.pool.tokens_info[token_in]
        y = self.pool.tokens_info[token_out]
        dy = order.token_volume

        if dy >= y:
            order.status = "Canceled"
            return

        # Расчёт dx: сколько нужно заплатить с учётом комиссии
        new_y = y - dy
        k = x * y
        new_x = k / new_y
        dx_without_fee = new_x - x
        dx = dx_without_fee / (1 - self.fee)

        if order.trader.portfolio[token_in] < dx:
            order.status = "Canceled"
            return

        # Обновление портфеля и пула
        order.trader.portfolio[token_in] -= dx
        order.trader.portfolio[token_out] += dy

        self.pool.tokens_info[token_in] += dx
        self.pool.tokens_info[token_out] -= dy

        order.status = "Succeed"

    def _sell_market(self, order: "Order"):
        token_in = order.token  # токен, который трейдер продаёт
        token_out = self._get_other_token(token_in)

        dx = order.token_volume
        if order.trader.portfolio[token_in] < dx:
            order.status = "Canceled"
            return

        x = self.pool.tokens_info[token_in]
        y = self.pool.tokens_info[token_out]

        # Учёт комиссии
        dx_with_fee = dx * (1 - self.fee)
        new_x = x + dx_with_fee
        k = x * y
        new_y = k / new_x
        dy = y - new_y

        if dy > y:
            order.status = "Canceled"
            return

        # Обновление портфеля и пула
        order.trader.portfolio[token_in] -= dx
        order.trader.portfolio[token_out] += dy

        self.pool.tokens_info[token_in] += dx
        self.pool.tokens_info[token_out] -= dy

        order.status = "Succeed"

    def get_price(self, token_in: str, token_out: str) -> float:
        x = self.pool.tokens_info[token_in]
        y = self.pool.tokens_info[token_out]
        if x == 0:
            return float('inf')
        return y / x

    def _process_limit_order(self, order: "Order", timestamp: int):
        if order.lifetime is not None and timestamp - order.creation_timestamp > order.lifetime:
            order.status = "Canceled"
            return
        token_in = order.token if order.operation_type == "SELL" else self._get_other_token(order.token)
        token_out = self._get_other_token(token_in)
        price = self.get_price(token_in, token_out)
        if order.operation_type == "BUY":
            if price <= order.limit_price:
                self._buy_market(order)
        else:
            if price >= order.limit_price:
                self._sell_market(order)

    def execute_order(self, order: "Order", timestamp: int):
        if order.status != "Awaiting":
            return

        if order.order_type == "Market":
            if order.operation_type == "BUY":
                self._buy_market(order)
            else:
                self._sell_market(order)
        elif order.order_type == "Limit":
            self._process_limit_order(order, timestamp)
        else:
            raise ValueError(f"Unsupported order type {order.order_type}.")
