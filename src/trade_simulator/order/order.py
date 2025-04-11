from typing import Optional

from trade_simulator.agents.basic_agent import BasicAgent
from trade_simulator.utils.consts import ORDER_OPERATION_STATUSES, ORDER_OPERATION_TYPES


class Order:
    def __init__(
        self,
        trader: BasicAgent,
        creation_timestamp: int,
        operation_type: str,
        token: str,
        token_volume: float,
        priority: int = 1,
        cancel_possibility: bool = True,
        lifetime: Optional[int] = None,
        status: str = "Awaiting",
    ):
        self.trader = trader
        self.creation_timestamp = creation_timestamp
        self.token = token
        self.cancel_possibility = cancel_possibility
        self.lifetime = lifetime
        self.token_volume = token_volume

        if priority < 1:
            raise (f"Order priority has to be more or equal to 1, got {priority}.")
        self.priority = priority

        if operation_type not in ORDER_OPERATION_TYPES:
            raise ValueError(f"Unsupported order operation type {operation_type}.")
        self.operation_type = operation_type

        if status not in ORDER_OPERATION_STATUSES:
            raise ValueError(f"Unsupported order status type {operation_type}.")
        self.status
