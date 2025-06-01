from trade_simulator.agents.basic_agent import BasicAgent
from trade_simulator.order.order import Order

class SimpleMarketMaker(BasicAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = "SimpleMarketMaker"
        self.pools = []
        self.rules = kwargs["rules"]