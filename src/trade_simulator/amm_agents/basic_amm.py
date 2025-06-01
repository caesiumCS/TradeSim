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
        random.shuffle(self.pool.order_book)
        self.pool.order_book = sorted(
            self.pool.order_book, key=lambda o: (o.creation_timestamp, o.priority)
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

    def execute_orders(self):
        self.sort_orders()
        for order in self.pool.order_book:
            self.execute_order(order)
        self.clean_order_book()
