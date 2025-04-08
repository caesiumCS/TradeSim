from abc import ABC, abstractmethod

class BasicAgent(ABC):
    def __init__(self, **kwargs):
        self.pools = {}

    @abstractmethod
    def run_agent_action(self, timestamp:int):
        pass

    @abstractmethod
    def check_settings(self, **kwargs):
        pass