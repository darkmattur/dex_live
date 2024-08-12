from ..base import BaseEdge
from .router import UniswapV3Router


class UniswapV3Edge(BaseEdge):
    _router_cls = UniswapV3Router

    def __init__(self, pool, token_in, token_out):
        super(UniswapV3Edge, self).__init__(pool, token_in, token_out)
        self.router = self._router_cls.get_router(pool.conn)
        self.swap_address = self.router.address

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

    def __repr__(self):
        return f'[{self.pool.conn.name}] {self.__class__.__name__} ({self.token_in.symbol}/{self.token_out.symbol}) @ {self.pool.fee}'
