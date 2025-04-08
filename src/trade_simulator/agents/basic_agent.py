from abc import ABC, abstractmethod


class BasicAgent(ABC):
    def __init__(self, **kwargs):
        # TODO - add basic kwargs checker
        # TODO - add metrics dict here
        self.pools = {}

    @abstractmethod
    def run_agent_action(self, timestamp: int):
        pass
