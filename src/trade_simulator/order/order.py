from typing import Optional

from trade_simulator.utils.consts import ORDER_OPERATION_TYPES


class Order:
    def __init__(
        self,
        trader_id: int,
        creation_timestamp: int,
        operation_type: str,
        token: str,
        priority: int = 1,
        cancel_possibility: bool = True,
        lifetime: Optional[int] = None,
    ):
        self.trader_id = trader_id
        self.creation_timestamp = creation_timestamp
        self.token = token
        self.priority = priority
        self.cancel_possibility = cancel_possibility
        self.lifetime = lifetime

        if operation_type not in ORDER_OPERATION_TYPES:
            raise ValueError(f"Unsupported operation type {operation_type}.")
        self.operation_type = operation_type
