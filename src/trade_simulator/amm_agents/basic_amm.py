from abc import ABC, abstractmethod

from trade_simulator.pool.pool import Pool


class AMM(ABC):
    def __init__(self, pool: Pool, **kwargs):
        self.pool = pool
        self.settings = kwargs

    @abstractmethod
    def complete_order(self):  # TODO - fix arguments
        pass

    @abstractmethod
    def sort_orders(self):  # TODO - fix arguments
        pass
