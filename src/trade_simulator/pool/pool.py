from typing import Any, Dict, Union


class Pool:
    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.name = kwargs["name"]

        self.tokens_info = self.create_tokens_pool(kwargs["tokens"])

    def generate_amm(self, amm_settings: Dict[str, Any]):
        pass

    def create_tokens_pool(
        self, tokens_info: Dict[str, Union[str, int]]
    ) -> Dict[str, int]:
        token_to_quantity = {}
        for token_info in tokens_info:
            token_to_quantity[token_info["name"]] = token_info["start_quantity"]
        return token_to_quantity
