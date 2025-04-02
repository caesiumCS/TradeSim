import pytest
import yaml

from trade_simulator.utils.utils import check_amm_settings
from trade_simulator.utils.utils import read_settings


def test_check_amm_settings():
    amm_settings = {}
    pool_settings = {}
    with pytest.raises(ValueError, match="Expected to have type of amm."):
        check_amm_settings(amm_settings, pool_settings)

    amm_settings["type"] = "Unsupported type"
    with pytest.raises(ValueError, match="Amm type 'Unsupported type' is not supported."):
        check_amm_settings(amm_settings, pool_settings)

    amm_settings["type"] = "Uniswap"
    pool_settings["tokens"] = []
    with pytest.raises(ValueError, match="For Uniswap type 2 tokens only required."):
        check_amm_settings(amm_settings, pool_settings)
    pool_settings["tokens"] = [1, 2]
    check_amm_settings(amm_settings, pool_settings)

def test_read_setting():
    path = "Unsupported_path"
    with pytest.raises(FileNotFoundError):
        read_settings(path)
    read_settings("simulation.yaml")