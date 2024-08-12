from ..base import BasePool
from .edge import UniswapV2Edge


class UniswapV2Pair(BasePool):
    _base_path = BasePool.clean_file_path(__file__)
    abi = BasePool.load_json(__file__, 'abi', 'pair.json')
    _events = ['Mint', 'Swap', 'Burn', 'Sync']
    fee = 30
    _edge_cls = UniswapV2Edge

    def __init__(self, chain, address, exchange, token_0=None, token_1=None):
        super(UniswapV2Pair, self).__init__(
            chain=chain, address=address, exchange=exchange)

        token_0 = self.conn.get_token(token_0)
        if token_0 is None:
            token_0 = self.conn.get_token_from_address(self.functions.token0())

        token_1 = self.conn.get_token(token_1)
        if token_1 is None:
            token_1 = self.conn.get_token_from_address(self.functions.token1())

        self._token_0, self._token_1 = token_0, token_1

        self._rate, self._liquidity = None, None
        self._token_0_liquidity, self._token_1_liquidity = None, None

    @property
    def rate(self): return self._rate

    @property
    def liquidity(self): return self._liquidity

    @property
    def token_0_liquidity(self): return self._token_0_liquidity

    @property
    def token_1_liquidity(self): return self._token_1_liquidity

    @property
    def token_0(self): return self._token_0

    @property
    def token_1(self): return self._token_1

    def update(self):
        """
        Updates the liquidity and rate of the pool
        """

        reserves_res = self.functions.getReserves()
        quote_reserve, base_reserve = reserves_res[0], reserves_res[1]

        adjusted_reserve0 = quote_reserve / (10 ** self._token_0.decimals)
        adjusted_reserve1 = base_reserve / (10 ** self._token_1.decimals)
        self._token_0_liquidity = adjusted_reserve0
        self._token_1_liquidity = adjusted_reserve1

        self._liquidity = adjusted_reserve1 * adjusted_reserve0

        if self.liquidity > 0:
            self._rate = adjusted_reserve1 / adjusted_reserve0
        else:
            self._rate = None
