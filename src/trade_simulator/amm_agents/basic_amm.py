import random
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from trade_simulator.order.order import Order
    from trade_simulator.pool.pool import Pool

from trade_simulator.utils.consts import ORDER_OPERATION_STATUSES


class AMM(ABC):
    def __init__(self, pool: "Pool", **kwargs):
        self.pool = pool
        self.settings = kwargs
        self.type = None

        self.fee = 0.0 if "fee" not in self.settings else self.settings["fee"]

    @abstractmethod
    def execute_order(self, order: "Order"):
        pass

    def sort_orders(self):
        # Перемешиваем для рандомного порядка среди ордеров с одинаковым временем и приоритетом
        random.shuffle(self.market_orders)
        random.shuffle(self.limit_orders)
        self.market_orders = sorted(
            self.market_orders, key=lambda o: (o.creation_timestamp, o.priority)
        )
        self.limit_orders = sorted(
            self.limit_orders, key=lambda o: (o.creation_timestamp, o.priority)
        )

    @abstractmethod
    def write_metrics(self):
        pass

    def clean_order_book(self):
        orders_to_statuses = {}
        for status in ORDER_OPERATION_STATUSES:
            orders_to_statuses[status] = []

        for order in self.pool.order_book:
            orders_to_statuses[order.status].append(order)

        for status in orders_to_statuses.keys():
            self.pool.metrics[f"number_of_{status}_orders_in_order_book"].append(
                len(orders_to_statuses[status])
            )

        self.pool.order_book = orders_to_statuses["Awaiting"]

    def get_orders_by_type(self):
        limit_orders = []
        market_orders = []
        for order in self.pool.order_book:
            if order.order_type == "Limit":
                limit_orders.append(order)
            elif order.order_type == "Market":
                market_orders.append(order)
        return limit_orders, market_orders

    @abstractmethod
    def _process_limit_order(self, order: "Order", timestamp: int):
        pass

    def process_limit_orders(self, timestamp: int):
        for order in self.limit_orders:
            if order.status == "Awaiting":
                self._process_limit_order(order, timestamp)

    def execute_orders(self, timestamp: int):
        self.limit_orders, self.market_orders = self.get_orders_by_type()
        self.sort_orders()
        self.process_limit_orders(timestamp)
        for order in self.market_orders:
            self.execute_order(order, timestamp)
            self.process_limit_orders(timestamp)
        self.clean_order_book()

    @abstractmethod
    def get_asset_price_in_currency(
        self, token_as_asset, token_as_currency, amount_of_asset=1.0
    ) -> float:
        pass
