from ..base import BasePool


class AlgebraDEXPool(BasePool):
    abi = BasePool.load_json(__file__, 'abi', 'pool.json')
    _events = ['Mint', 'Swap', 'Burn', 'Flash', 'Fee']

    def __init__(self, chain, address, exchange, token_0=None, token_1=None,):
        super(AlgebraDEXPool, self).__init__(chain=chain, address=address, exchange=exchange)

        token_0 = self.conn.get_token(token_0)
        if token_0 is None:
            token_0 = self.conn.get_token_from_address(self.functions.token0())

        token_1 = self.conn.get_token(token_1)
        if token_1 is None:
            token_1 = self.conn.get_token_from_address(self.functions.token1())

        self._token_1, self._token_0 = token_1, token_0

        self._rate, self._liquidity = None, None
        self.tick = None
        self.fee = None

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
        sqrt_price_x96, tick, _, fee_hbp, _, _, _, _ = self.functions.globalState()

        self.tick = tick
        decimal_ratio = pow(10, self._token_0.decimals - self._token_1.decimals)
        price = (sqrt_price_x96 / pow(2, 96)) ** 2

        self._rate = price * decimal_ratio if self._liquidity > 0 else None
        self.fee = fee_hbp / 100

    def __repr__(self):
        return f'[{self.conn.name}] {self.__class__.__name__} ({self._token_1.symbol}/{self._token_0.symbol})'
