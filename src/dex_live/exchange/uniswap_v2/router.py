import time

from ..base import BaseRouter


class UniswapV2Router(BaseRouter):
    _config = BaseRouter.load_yml(__file__, 'config.yml')
    abi = BaseRouter.load_json(__file__, 'abi', 'router_2.json')

    router_index = 'router_2'

    def build_swap_transaction(self, wallet, edge, amount, max_slippage=100.0, **kwargs):
        """
        Approves swap transaction with the Unsiwap order router

        Parameters
        ----------
        wallet : BaseWallet object
            initiated wallet
        edge :
            pool to be traded
        amount : float
            total amount of tokens to be traded (non-decimal)
        max_slippage : float
            maximum slippage to accept at transaction

        Returns
        -------
        string
            transaction hash
        """
        amount_decimals = edge.token_in.token_to_decimals(amount)
        min_out = int(edge.rate * (10_000 - max_slippage) * amount_decimals) // 10_000

        return self._contract.functions.swapExactTokensForTokens(
            amount_decimals,  # amountIn
            min_out,  # amountOutMin
            (edge.token_in.address, edge.token_out.address),  # path
            wallet.address,  # to
            int(time.time() + self.timeout)  # deadline
        )
