from typing import TYPE_CHECKING
import math

from trade_simulator.amm_agents.basic_amm import AMM

if TYPE_CHECKING:
    from trade_simulator.order.order import Order
    from trade_simulator.pool.pool import Pool


class ProductInvariantAMM(AMM):
    def __init__(self, pool: "Pool", **kwargs):
        super().__init__(pool, **kwargs)

        self.type = "ProductInvariant"
        self.tokens = list(self.pool.tokens_info.keys())

        self.pool.metrics["k"] = []
        for token in self.tokens:
            for other in self.tokens:
                if token != other:
                    self.pool.metrics[f"price_of_{token}_in_{other}"] = []

        self._write_k_metric()

    def _write_k_metric(self):
        k = self._calculate_k()
        self.pool.metrics["k"].append(k)

    def write_metrics(self):
        self._write_k_metric()
        for token_in in self.tokens:
            for token_out in self.tokens:
                if token_in != token_out:
                    try:
                        price = self.get_asset_price_in_currency(token_in, token_out)
                        self.pool.metrics[f"price_of_{token_in}_in_{token_out}"].append(price)
                    except Exception:
                        self.pool.metrics[f"price_of_{token_in}_in_{token_out}"].append(None)

    def _calculate_k(self):
        k = 1.0
        for balance in self.pool.tokens_info.values():
            k *= balance
        return k

    def _get_output_amount(self, token_in: str, token_out: str, dx: float) -> float:
        """
        Вычисляет, сколько можно получить token_out за dx token_in.
        """
        reserves = self.pool.tokens_info.copy()
        reserves[token_in] += dx * (1 - self.fee)  # учёт комиссии

        k = self._calculate_k()

        # Чисто математически, найдём dy, чтобы новый k оставался прежним
        # new_k = (x + dx * fee) * y' * z' * ... = k
        # => y' = k / (x + dx * fee * prod остальных)

        denominator = 1.0
        for token, amount in reserves.items():
            if token != token_out:
                denominator *= amount

        new_token_out_balance = k / denominator
        dy = self.pool.tokens_info[token_out] - new_token_out_balance

        if dy < 0 or dy > self.pool.tokens_info[token_out]:
            raise ValueError("Invalid output amount computed.")

        return dy

    def get_asset_price_in_currency(self, token_as_asset: str, token_as_currency: str, amount_of_asset: float = 1.0) -> float:
        dy = amount_of_asset
        dx = self._get_input_amount(token_as_currency, token_as_asset, dy)
        return dx / dy

    def _get_input_amount(self, token_in: str, token_out: str, dy: float) -> float:
        """
        Вычисляет, сколько нужно token_in, чтобы получить dy token_out.
        """
        if dy >= self.pool.tokens_info[token_out]:
            raise ValueError("Not enough liquidity")

        k = self._calculate_k()

        reserves = self.pool.tokens_info.copy()
        reserves[token_out] -= dy

        denominator = 1.0
        for token, amount in reserves.items():
            if token != token_in:
                denominator *= amount

        new_token_in_balance = k / denominator
        dx_without_fee = new_token_in_balance - self.pool.tokens_info[token_in]
        dx = dx_without_fee / (1 - self.fee)
        return dx

    def _buy_market(self, order: "Order"):
        token_out = order.token
        token_in = next(t for t in self.tokens if t != token_out)

        dy = order.token_volume

        if dy >= self.pool.tokens_info[token_out]:
            order.status = "Canceled"
            return

        try:
            dx = self._get_input_amount(token_in, token_out, dy)
        except ValueError:
            order.status = "Canceled"
            return

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
        token_in = order.token
        token_out = next(t for t in self.tokens if t != token_in)

        dx = order.token_volume
        if order.trader.portfolio[token_in] < dx:
            order.status = "Canceled"
            return

        try:
            dy = self._get_output_amount(token_in, token_out, dx)
        except ValueError:
            order.status = "Canceled"
            return

        if dy > self.pool.tokens_info[token_out]:
            order.status = "Canceled"
            return

        order.trader.portfolio[token_in] -= dx
        order.trader.portfolio[token_out] += dy
        self.pool.tokens_info[token_in] += dx
        self.pool.tokens_info[token_out] -= dy

        order.status = "Succeed"

    def get_price(self, token_in: str, token_out: str) -> float:
        return self.get_asset_price_in_currency(token_in, token_out)

    def _process_limit_order(self, order: "Order", timestamp: int):
        if order.lifetime is not None and timestamp - order.creation_timestamp > order.lifetime:
            order.status = "Canceled"
            return

        token_in = order.token if order.operation_type == "SELL" else next(t for t in self.tokens if t != order.token)
        token_out = next(t for t in self.tokens if t != token_in)
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
        
    def _get_other_token(self, token: str) -> list[str]:
        return [t for t in self.tokens if t != token]

