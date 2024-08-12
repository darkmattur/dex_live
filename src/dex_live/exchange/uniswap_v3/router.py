from ..base import BaseRouter


class UniswapV3Router(BaseRouter):
    abi = BaseRouter.load_json(__file__, 'abi', 'router.json')
    _config = BaseRouter.load_yml(__file__, 'config.yml')
    router_index = 'router_2'

    def build_swap_transaction(self, wallet, edge, amount, max_slippage=100.0, **kwargs):
        amount_decimals = edge.token_in.token_to_decimals(amount)
        fee_bps = edge.pool.fee * 100
        min_out = int(edge.rate * (10_000 - max_slippage) * amount_decimals) // 10_000

        return self._contract.functions.exactInputSingle({
            "tokenIn": edge.token_in.address,
            "tokenOut": edge.token_out.address,
            "fee": fee_bps,
            "recipient": wallet.address,
            "amountIn": amount_decimals,
            "amountOutMinimum": min_out,
            "sqrtPriceLimitX96": 0
        })
