from abc import ABC, abstractmethod

class BasicAgent(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def run_agent_action(self, timestamp:int):
        pass