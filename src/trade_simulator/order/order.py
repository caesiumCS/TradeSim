from trade_simulator.utils.consts import ORDER_OPERATION_TYPES

class Order:
    def __init__(self,
                 trader_id:int,
                 timestamp:int,
                 operation_type: str,
                 token: str,
                 priority:int = 1):
        self.trader_id = trader_id
        self.timestamp = timestamp
        self.token = token
        self.priority = priority

        if operation_type not in ORDER_OPERATION_TYPES:
            raise ValueError(f"Unsupported operation type {operation_type}.")
        self.operation_type = operation_type