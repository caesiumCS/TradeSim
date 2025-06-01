from trade_simulator.agents.basic_agent import BasicAgent
from trade_simulator.order.order import Order

class SimpleMarketMaker(BasicAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.type = "SimpleMarketMaker"
        self.pools = {}
        self.rules = kwargs["rules"]
        for rule in self.rules:
            rule["steps_without_action"] = 0

    def run_agent_action(self, timestamp: int):
        pass