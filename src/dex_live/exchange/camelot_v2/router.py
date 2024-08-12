import time

from ..uniswap_v2 import UniswapV2Router


class CamelotV2Router(UniswapV2Router):
    _config = UniswapV2Router.load_yml(__file__, 'config.yml')
    abi = UniswapV2Router.load_json(__file__, 'abi', 'router.json')
    router_index = 'router'

    def build_swap_transaction(self, wallet, edge, amount, max_slippage=100.0, **kwargs):
        amount_decimals = edge.token_in.token_to_decimals(amount)
        min_out = int(edge.rate * (10_000 - max_slippage) * amount_decimals) // 10_000

        return self._contract.functions.swapExactTokensForTokensSupportingFeeOnTransferTokens(
            amount_decimals,  # amountIn
            min_out,  # amountOutMin
            (edge.token_in.address, edge.token_out.address),  # path
            wallet.address,  # to
            self.ADDRESS_ZERO,  # referrer
            int(time.time() + self.timeout)  # deadline
        )
