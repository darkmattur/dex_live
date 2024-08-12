import abc
from functools import lru_cache

from .. import BaseContract, ChainManager, BaseChain


class BaseRouter(BaseContract):
    _chain_manager = ChainManager()
    timeout = 10

    @property
    @abc.abstractmethod
    def _config(self):
        pass

    @property
    @abc.abstractmethod
    def router_index(self):
        pass

    def __init__(self, chain):
        if not isinstance(chain, BaseChain):
            chain = self._chain_manager.get_chain(chain)

        if chain.name not in self._config:
            raise ValueError(f'Chain {chain.name} not in config for {self}')
        address = self._config[chain.name][self.router_index]

        super(BaseRouter, self).__init__(chain=chain, address=address)

    @abc.abstractmethod
    def build_swap_transaction(self, wallet, edge, amount, max_slippage=100.0, **kwargs):
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}'

    @classmethod
    @lru_cache(maxsize=None)
    def get_router(cls, chain):
        if not isinstance(chain, BaseChain):
            chain = cls._chain_manager.get_chain(chain)

        return cls(chain=chain)

    # TODO: Create intelligent routing
    # def _unpack_args(self, pools, **kwargs):
    #     if isinstance(pools, BasePool):
    #         pools = [(pools, kwargs['long'])]
    #
    #     # Determine token path
    #     td_tuples = sum([
    #         (pool.quote, pool.base) if long else (pool.base, pool.quote)
    #         for pool, long, amount in pools
    #     ], [])
    #
    #     assert all([t_c == t_n for (_, t_c), (t_n, _) in zip(td_tuples, td_tuples[1:])])
    #
    #     s_token, _ = td_tuples[0]
    #     path = [s_token] + [n_token for _, n_token in td_tuples]
    #
    #     # Calculate slippage
    #     max_slippage = kwargs.get('max_slippage', 1.0) / 100
    #     min_amount_out = pow(1.0 - max_slippage, len(path) - 1)
    #
    #     return path, min_amount_out
