from trade_simulator.agents.basic_agent import BasicAgent


class SinglePoolRandomTrader(BasicAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # TODO - check input parameters

        self.portfolio = kwargs["portfolio"]
        self.steps_to_make_new_transaction = kwargs["steps_to_make_new_transaction"]
        self.pool_id = [kwargs["pool_id"]]

    def run_agent_action(self, timestamp: int):
        pass
