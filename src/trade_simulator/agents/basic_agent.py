from abc import ABC, abstractmethod


class BasicAgent(ABC):
    def __init__(self, **kwargs):
        # TODO - add basic kwargs checker
        self.pools = {}
        self.metrics = {
            "portfolio": {},
        }
        self.parse_portfolio(kwargs["portfolio"])

    @abstractmethod
    def run_agent_action(self, timestamp: int):
        pass

    def parse_portfolio(self, input_portfolio):
        self.portfolio = {}
        for el in input_portfolio:
            self.portfolio[el["name"]] = el["quantity"]
            self.metrics["portfolio"][el["name"]] = [el["quantity"]]

    def update_metrics(self):
        for token in self.portfolio.keys():
            self.metrics["portfolio"][token].append(self.portfolio[token])
