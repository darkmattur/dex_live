import abc

from ..base import BaseEdge


class AlgebraDexEdge(BaseEdge):
    @property
    @abc.abstractmethod
    def _router_cls(self):
        pass

    def __init__(self, pool, token_in, token_out):
        super(AlgebraDexEdge, self).__init__(pool, token_in, token_out)
        self.router = self._router_cls.get_router(pool.conn)
        self.swap_address = self.router.address

    def swap(self, wallet, amount, max_slippage=100.0, **kwargs):
        return wallet.execute(
            transaction=self.router.build_swap_transaction(
                wallet=wallet, edge=self, amount=amount, max_slippage=max_slippage, **kwargs
            )
        )
