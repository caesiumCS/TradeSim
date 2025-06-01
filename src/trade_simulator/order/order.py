from typing import Optional

from trade_simulator.agents.basic_agent import BasicAgent
from trade_simulator.utils.consts import ORDER_OPERATION_TYPES, ORDER_TYPES


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
        order_type: str = "Market",
        limit_price: Optional[float] = None,
    ):
        self.trader = trader
        self.creation_timestamp = creation_timestamp
        self.token = token
        self.cancel_possibility = cancel_possibility
        self.lifetime = lifetime
        self.token_volume = token_volume
        self.priority = priority
        self.operation_type = operation_type
        self.status = "Awaiting"
        self.order_type = order_type
        self.limit_price = limit_price
        self.check_order_fields()

    def check_order_fields(self):
        if self.priority < 1:
            raise (f"Order priority has to be more or equal to 1, got {self.priority}.")
        if self.operation_type not in ORDER_OPERATION_TYPES:
            raise ValueError(f"Unsupported order operation type {self.operation_type}.")
        if self.order_type not in ORDER_TYPES:
            raise ValueError(f"Unsupported order type {self.order_type}.")
