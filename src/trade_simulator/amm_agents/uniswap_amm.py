from typing import TYPE_CHECKING

from trade_simulator.amm_agents.basic_amm import AMM

if TYPE_CHECKING:
    from trade_simulator.order.order import Order
    from trade_simulator.pool.pool import Pool


class UniswapAMM(AMM):
    def __init__(self, pool: "Pool", **kwargs):
        super().__init__(pool, **kwargs)

    def execute_order(self, order: "Order"):  # TODO - fix arguments
        pass

    def sort_orders(self):
        pass
