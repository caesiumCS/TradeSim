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
        self.pool.metrics[f"price_of_{self.token_a}_{self.token_b}"] = []
        self.pool.metrics[f"price_of_{self.token_b}_{self.token_a}"] = []
        self.pool.metrics["k"].append(
            self.pool.tokens_info[self.token_a] * self.pool.tokens_info[self.token_b]
        )
        self.pool.metrics["profit_from_fees"] = {}
        for token in tokens:
            self.pool.metrics["profit_from_fees"][token] = {"timestamp": [0], "value": [0]}

    def write_metrics(self):
        self.pool.metrics["k"].append(
            self.pool.tokens_info[self.token_a] * self.pool.tokens_info[self.token_b]
        )
        self.pool.metrics[f"price_of_{self.token_a}_{self.token_b}"].append(
            self.get_asset_price_in_currency(self.token_a, self.token_b)
        )
        self.pool.metrics[f"price_of_{self.token_b}_{self.token_a}"].append(
            self.get_asset_price_in_currency(self.token_b, self.token_a)
        )

    def _buy_market(self, order: "Order", timestamp: int):
        token_out = order.token  # токен, который трейдер хочет получить
        token_in = order.second_token

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

        if self.pool.metrics["profit_from_fees"][token_in]["timestamp"][-1] != timestamp:
            self.pool.metrics["profit_from_fees"][token_in]["timestamp"].append(
                timestamp)
            self.pool.metrics["profit_from_fees"][token_in]["value"].append(0)
            self.pool.metrics["profit_from_fees"][token_in]["value"][-1] += self.pool.metrics["profit_from_fees"][token_in]["value"][-2]
        self.pool.metrics["profit_from_fees"][token_in]["value"][-1] += dx - dx_without_fee


        # Обновление портфеля и пула
        order.trader.portfolio[token_in] -= dx
        order.trader.portfolio[token_out] += dy

        self.pool.tokens_info[token_in] += dx
        self.pool.tokens_info[token_out] -= dy

        order.status = "Succeed"

    def _sell_market(self, order: "Order", timestamp: int):
        token_in = order.token  # токен, который трейдер продаёт
        token_out = order.second_token

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

        if self.pool.metrics["profit_from_fees"][token_in]["timestamp"][-1] != timestamp:
            self.pool.metrics["profit_from_fees"][token_in]["timestamp"].append(
                timestamp)
            self.pool.metrics["profit_from_fees"][token_in]["value"].append(0)
            self.pool.metrics["profit_from_fees"][token_in]["value"][-1] += self.pool.metrics["profit_from_fees"][token_in]["value"][-2]
        self.pool.metrics["profit_from_fees"][token_in]["value"][-1] += abs(dx_with_fee - dx)

        # Обновление портфеля и пула
        order.trader.portfolio[token_in] -= dx
        order.trader.portfolio[token_out] += dy

        self.pool.tokens_info[token_in] += dx
        self.pool.tokens_info[token_out] -= dy

        order.status = "Succeed"

    def get_asset_price_in_currency(
        self, token_as_asset: str, token_as_currency: str, amount_of_asset: float = 1.0
    ) -> float:

        token_as_asset_count = self.pool.tokens_info[token_as_asset]
        token_as_currency_count = self.pool.tokens_info[token_as_currency]

        if amount_of_asset >= token_as_asset_count:
            raise ValueError(
                f"Not enough {token_as_asset} in the pool to get price for {amount_of_asset} {token_as_asset}."
            )

        fee_multiplier = 1 - self.fee
        numerator = token_as_currency_count * amount_of_asset
        denominator = (token_as_asset_count - amount_of_asset) * fee_multiplier

        return numerator / denominator

    def get_price(self, token_in: str, token_out: str) -> float:
        x = self.pool.tokens_info[token_in]
        y = self.pool.tokens_info[token_out]
        if x == 0:
            return float("inf")
        return y / x

    def _process_limit_order(self, order: "Order", timestamp: int):
        if (
            order.lifetime is not None
            and timestamp - order.creation_timestamp > order.lifetime
        ):
            order.status = "Canceled"
            return
        token_in = (
            order.token
            if order.operation_type == "SELL"
            else order.second_token
        )
        token_out = order.second_token if order.operation_type == "SELL" else order.token
        price = self.get_price(token_in, token_out)
        if order.operation_type == "BUY":
            if price <= order.limit_price:
                self._buy_market(order, timestamp)
        else:
            if price >= order.limit_price:
                self._sell_market(order, timestamp)

    def execute_order(self, order: "Order", timestamp: int):
        if order.status != "Awaiting":
            return

        if order.order_type == "Market":
            if order.operation_type == "BUY":
                self._buy_market(order, timestamp)
            else:
                self._sell_market(order, timestamp)
        elif order.order_type == "Limit":
            self._process_limit_order(order, timestamp)
        else:
            raise ValueError(f"Unsupported order type {order.order_type}.")
