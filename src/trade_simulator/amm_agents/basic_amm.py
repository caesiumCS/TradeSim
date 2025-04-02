from abc import ABC, abstractmethod

from trade_simulator.order.order import Order
from trade_simulator.pool.pool import Pool
from trade_simulator.utils.consts import ORDER_OPERATION_STATUSES


class AMM(ABC):
    def __init__(self, pool: Pool, **kwargs):
        self.pool = pool
        self.settings = kwargs

    @abstractmethod
    def execute_order(self, order: Order):  # TODO - fix arguments
        pass

    @abstractmethod
    def sort_orders(self):
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
