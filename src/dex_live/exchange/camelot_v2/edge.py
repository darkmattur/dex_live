from .router import CamelotV2Router

from ..uniswap_v2 import UniswapV2Edge


class CamelotV2Edge(UniswapV2Edge):
    _router_cls = CamelotV2Router

    def __init__(self, pool, token_in, token_out):
        super(CamelotV2Edge, self).__init__(pool, token_in, token_out)

    @property
    def rate(self):
        if self.pool.rate is None:
            return None

        if self.long:
            return (10000 - self.pool.token_0_fee) * self.pool.rate / 10000
        else:
            return (10000 - self.pool.token_1_fee) / (self.pool.rate * 10000)

    @property
    def fee(self):
            return self.pool.token_0_fee if self.long else self.pool.token_1_fee

    def calculate_received_amount(self, amount):
        if self.long:
            x, y = self.pool.token_0_liquidity, self.pool.token_1_liquidity
        else:
            x, y = self.pool.token_1_liquidity, self.pool.token_0_liquidity

        amount_after_fee = (1 - (self.fee / 10000)) * amount

        return (y * amount_after_fee) / (x + amount_after_fee)
