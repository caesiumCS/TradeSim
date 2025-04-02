from abc import ABC, abstractmethod

from trade_simulator.pool.pool import Pool
from trade_simulator.order.order import Order


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

    @abstractmethod
    def clean_order_book(self):
        pass

    def execute_orders(self):
        self.sort_orders()
        for order in self.pool.order_book:
            self.execute_order(order)
        self.clean_order_book()
