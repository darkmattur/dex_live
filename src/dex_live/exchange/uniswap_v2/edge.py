from ..base import BaseEdge
from .router import UniswapV2Router


class UniswapV2Edge(BaseEdge):
    _router_cls = UniswapV2Router

    def __init__(self, pool, token_in, token_out):
        super(UniswapV2Edge, self).__init__(pool, token_in, token_out)
        self.router = self._router_cls.get_router(pool.conn)
        self.swap_address = self.router.address

    @property
    def liquidity(self):
        return self.pool.liquidity

    def swap(self, wallet, amount, max_slippage=100.0, **kwargs):
        """
        Approves swap transaction with the Unsiwap order router

        Parameters
        ----------
        wallet : BaseWallet object
            initiated wallet
        amount : float
            total amount of tokens to be traded (non-decimal)
        max_slippage : float
            maximum slippage to accept at transaction in basis points

        Returns
        -------
        string
            transaction hash
        """

        return wallet.execute(
            transaction=self.router.build_swap_transaction(
                wallet=wallet, edge=self, amount=amount, max_slippage=max_slippage, **kwargs
            )
        )

    def calculate_received_amount(self, amount):
        if self.long:
            x, y = self.pool.token_0_liquidity, self.pool.token_1_liquidity
        else:
            x, y = self.pool.token_1_liquidity, self.pool.token_0_liquidity

        amount_after_fee = (1 - (self.pool.fee / 10000)) * amount

        return (y * amount_after_fee) / (x + amount_after_fee)
