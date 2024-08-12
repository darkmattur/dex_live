import abc
from functools import cache

from .. import BaseContract
from .. import ChainManager


class BasePool(BaseContract):
    _chain_manager = ChainManager()
    fee = None

    def __init__(self, chain, address, exchange):
        if isinstance(chain, str):
            chain = self._chain_manager.get_chain(chain)
        super(BasePool, self).__init__(chain=chain, address=address)
        self.exchange = exchange

    @property
    @abc.abstractmethod
    def _edge_cls(self): pass

    @property
    @abc.abstractmethod
    def token_1(self): pass

    @property
    @abc.abstractmethod
    def token_0(self): pass

    @property
    @abc.abstractmethod
    def rate(self): pass

    @property
    @abc.abstractmethod
    def _events(self): pass

    @cache
    def get_edges(self):
        """
        Returns a tuple of the edge class relating to the pool.

        :returns: Edges generated from the given pool
        :rtype: tuple of BaseEdge
        """
        return (
            self._edge_cls(self, self.token_1, self.token_0),
            self._edge_cls(self, self.token_0, self.token_1)
        )

    # Methods for handling Memorization
    def update(self):
        pass

    def __repr__(self):
        return f'[{self.conn}] {self.__class__.__name__} ({self.token_1.symbol}/{self.token_0.symbol})'
