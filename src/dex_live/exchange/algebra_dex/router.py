import time

from ..base import BaseRouter


class AlgebraDexRouter(BaseRouter):
    abi = BaseRouter.load_json(__file__, 'abi', 'router.json')

    def build_swap_transaction(self, wallet, edge, amount, max_slippage=100.0, **kwargs):
        amount_decimals = edge.token_in.token_to_decimals(amount)
        min_out = int(edge.rate * (10_000 - max_slippage) * amount_decimals) // 10_000

        return self._contract.functions.exactInputSingle({
            "tokenIn": edge.token_in.address,
            "tokenOut": edge.token_out.address,
            "recipient": wallet.address,
            "deadline": int(time.time() + self.timeout),
            "amountIn": amount_decimals,
            "amountOutMinimum": min_out,
            "sqrtPriceLimitX96": 0
        })
