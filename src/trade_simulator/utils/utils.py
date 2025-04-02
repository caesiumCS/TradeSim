from typing import Any, Dict, Optional

import yaml

from trade_simulator.utils.consts import AMM_TYPES


def read_settings(path: str) -> Optional[Dict[str, Any]]:
    data = None
    with open(path, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return data


def check_amm_settings(amm_settings: Dict[str, Any], pool_settings: Dict[str, Any]):
    if amm_settings.get("type") is None:
        raise ValueError("Expected to have type of amm.")

    amm_type = amm_settings["type"]
    if amm_type not in AMM_TYPES:
        raise ValueError(f"Amm type {amm_type} is not supported.")

    if amm_type == "Uniswap" and len(pool_settings["tokens"]) != 2:
        raise ValueError(f"For {amm_type} type 2 tokens only required.")


def check_pools_settings(pools_settings: Dict[str, Any]):
    pools_settings = pools_settings["pools"]
    ids = []
    for settings in pools_settings:
        pool_id = settings["id"]

        if settings.get("steps_to_check_orderbook") is None:
            raise ValueError(
                "Expecting parameter 'steps_to_check_orderbook' in pool settings."
            )
        steps_to_check_orderbook = settings["steps_to_check_orderbook"]
        if steps_to_check_orderbook < 1:
            raise ValueError(
                f"Parameter 'steps_to_check_orderbook' has to be more or equal to 1, got {steps_to_check_orderbook}."
            )

        if settings.get("step_to_start_simulation") is None:
            raise ValueError(
                "Expecting parameter 'step_to_start_simulation' in pool settings."
            )
        step_to_start_simulation = settings["step_to_start_simulation"]
        if step_to_start_simulation < 0:
            raise ValueError(
                f"Parameter 'steps_to_check_orderbook' has to be more or equal to 0, got {step_to_start_simulation}."
            )

        if settings.get("amm_settings") is None:
            raise ValueError(
                f"Pool with id: {pool_id} is expected "
                "to have an 'amm_settings' field."
            )
        check_amm_settings(settings["amm_settings"], settings)

        if pool_id in ids:
            raise ValueError(f"Found identical pool id: {pool_id}.")
        ids.append(pool_id)

        if len(settings["tokens"]) < 2:
            raise ValueError(
                f"Pool with id: {pool_id} is expected"
                " to have more or equal than 2 tokens."
            )

        token_names = []
        for token in settings["tokens"]:
            name = token["name"]
            if name in token_names:
                raise ValueError(
                    f"Found identical token name in pool with id: {pool_id}."
                )
            token_names.append(token)

            if token["start_quantity"] <= 0:
                raise ValueError("Start token quantity has to be more than zero.")
