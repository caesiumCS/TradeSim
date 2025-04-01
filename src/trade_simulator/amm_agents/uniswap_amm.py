from trade_simulator.amm_agents.basic_amm import AMM
from trade_simulator.pool.pool import Pool

class UniswapAMM(AMM):
    def __init__(self, pool: Pool, **kwargs):
        super().__init__(pool, **kwargs)