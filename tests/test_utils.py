import pytest

from trade_simulator.utils.utils import (
    check_amm_settings,
    check_pool_tokens_settings,
    check_pools_settings,
    read_settings,
)


def test_check_amm_settings():
    amm_settings = {}
    pool_settings = {}
    with pytest.raises(ValueError, match="Expected to have type of amm."):
        check_amm_settings(amm_settings, pool_settings)

    amm_settings["type"] = "Unsupported type"
    with pytest.raises(
        ValueError, match="Amm type 'Unsupported type' is not supported."
    ):
        check_amm_settings(amm_settings, pool_settings)

    amm_settings["type"] = "UniswapV2"
    pool_settings["tokens"] = []
    with pytest.raises(ValueError, match="For UniswapV2 type 2 tokens only required."):
        check_amm_settings(amm_settings, pool_settings)
    pool_settings["tokens"] = [1, 2]
    check_amm_settings(amm_settings, pool_settings)


def test_read_setting():
    path = "Unsupported_path"
    with pytest.raises(FileNotFoundError):
        read_settings(path)
    read_settings("simulation.yaml")


def test_check_pool_tokens_settings():
    pool_id = 1
    settings = []
    with pytest.raises(
        ValueError,
        match="Pool with id: 1 is expected " "to have more or equal than 2 tokens.",
    ):
        check_pool_tokens_settings(settings, pool_id)
    settings = [
        {"name": "name1", "start_quantity": 0},
        {"name": "name1", "start_quantity": 100},
    ]
    with pytest.raises(
        ValueError, match="Start token quantity has to be more than zero."
    ):
        check_pool_tokens_settings(settings, pool_id)
    settings[0]["start_quantity"] = 1000
    with pytest.raises(
        ValueError, match="Found identical token name in pool with id: 1."
    ):
        check_pool_tokens_settings(settings, pool_id)
    settings[0]["name"] = "name2"
    check_pool_tokens_settings(settings, pool_id)


def test_check_pool_settings():
    pools_settings = {"pools": [{"id": 1}]}
    with pytest.raises(
        ValueError,
        match="Expecting parameter 'steps_to_check_orderbook' in pool settings.",
    ):
        check_pools_settings(pools_settings)
    pools_settings["pools"][0]["steps_to_check_orderbook"] = 0
    with pytest.raises(
        ValueError,
        match="Parameter 'steps_to_check_orderbook' has to be more or equal to 1, got 0.",
    ):
        check_pools_settings(pools_settings)
    pools_settings["pools"][0]["steps_to_check_orderbook"] = 5

    with pytest.raises(
        ValueError,
        match="Expecting parameter 'step_to_start_simulation' in pool settings.",
    ):
        check_pools_settings(pools_settings)
    pools_settings["pools"][0]["step_to_start_simulation"] = -1
    with pytest.raises(
        ValueError,
        match="Parameter 'steps_to_check_orderbook' has to be more or equal to 0, got -1.",
    ):
        check_pools_settings(pools_settings)
    pools_settings["pools"][0]["step_to_start_simulation"] = 5
