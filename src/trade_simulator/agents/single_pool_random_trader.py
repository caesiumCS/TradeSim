from trade_simulator.agents.basic_agent import BasicAgent

class SinglePoolRandomTrader(BasicAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.chance_to_action = kwargs["chance_to_action"]
        self.portfolio = kwargs["portfolio"]
        self.pool_id = [kwargs["pool_id"]]

    def check_settings(self, **kwargs):
        self.chance_to_action = kwargs["chance_to_action"]
        if self.chance_to_action <= 0 or self.chance_to_action > 100:
            raise ValueError(f"Got 'chance_to_action' equal to {self.chance_to_action}.")


    def run_agent_action(self, timestamp:int):
        pass