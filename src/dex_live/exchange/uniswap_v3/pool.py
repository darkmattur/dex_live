from ..base import BasePool
from .edge import UniswapV3Edge


class UniswapV3Pool(BasePool):
    _base_path = BasePool.clean_file_path(__file__)
    abi = BasePool.load_json(__file__, 'abi', 'pool.json')
    _events = ['Mint', 'Swap', 'Burn', 'Flash']
    _edge_cls = UniswapV3Edge

    def __init__(self, chain, address, exchange, fee=None, token_0=None, token_1=None):
        super(UniswapV3Pool, self).__init__(
            chain=chain, address=address, exchange=exchange)

        # Load tokens, use contract if not provided.
        token_0 = self.conn.get_token(token_0)
        if token_0 is None:
            token_0 = self.conn.get_token_from_address(self.functions.token0())

        token_1 = self.conn.get_token(token_1)
        if token_1 is None:
            token_1 = self.conn.get_token_from_address(self.functions.token1())

        self._token_1, self._token_0 = token_1, token_0

        if fee is None:
            fee = self.functions.fee() / 100
        self.fee = fee

        self._rate, self._liquidity = None, None
        self.tick = None

    @property
    def rate(self): return self._rate

    @property
    def liquidity(self): return self._liquidity

    @property
    def token_0(self): return self._token_0

    @property
    def token_1(self): return self._token_1

    def update(self):
        self._liquidity = self.functions.liquidity()
        sqrt_price_x96, tick, _, _, _, _, _ = self.functions.slot0()

        self.tick = tick
        decimal_ratio = pow(10, self._token_0.decimals - self._token_1.decimals)
        price = (sqrt_price_x96 / pow(2, 96)) ** 2

        self._rate = price * decimal_ratio if self._liquidity > 0 else None

    def __repr__(self):
        return f'[{self.conn.name}] {self.__class__.__name__} ({self.base.symbol}/{self.quote.symbol}) {self.fee}'
