import abc
from multiprocessing.pool import ThreadPool
import threading
import time

import pandas as pd
from tqdm import tqdm
import itertools

from .. import BaseContract, ChainManager, BaseChain, BaseToken


class BaseFactory(BaseContract, threading.Thread):
    _address_book_columns = ['address', 'token_0', 'token_1']
    _chain_manager = ChainManager()

    daemon = True
    _interval = 0.5
    _processes = 4

    @property
    @abc.abstractmethod
    def _base_path(self):
        pass

    @property
    @abc.abstractmethod
    def abi(self):
        pass

    @property
    @abc.abstractmethod
    def _config(self):
        pass

    @property
    @abc.abstractmethod
    def _pool_cls(self):
        pass

    def __init__(self, chain):
        # Initialise super class
        if isinstance(chain, str):
            chain = self._chain_manager.get_chain(chain)
        if chain.name not in self._config:
            raise NotImplementedError(
                f'Unable to load config for chain "{chain.name}" for "{self.__class__.__name__}"!')

        config = self._config[chain.name]
        super(BaseFactory, self).__init__(chain=chain, address=config['factory'])

        self._stop_event = threading.Event()

        # Load address book into memory
        self.address_book = self._load_address_book()
        self._pools = dict()

        # Initialise memorised pools from definition
        for _, pool_def in self.address_book.iterrows():
            self._pools[self.get_key(**pool_def)] = self._pool_cls(chain=self.conn, exchange=self, **pool_def)

        with ThreadPool(processes=self._processes) as pool:
            list(tqdm(
                iterable=pool.imap(func=lambda pool_: pool_.update(), iterable=self._pools.values()),
                desc=f'Initialising {self} pools',
                total=len(self._pools)
            ))

        self.edges = list(itertools.chain(*[
            pool.get_edges() for pool in self._pools.values()
        ]))

    def __post_init__(self):
        self.start()

    def get_key(self, token_0, token_1, **kwargs):
        """
        Taking the pool definition as an input, returns the key of the corresponding pool.

        :return: tuple
        """
        return token_0, token_1

    def get_pool_from_address(self, address):
        matches_ = self.address_book[self.address_book['address'] == address]
        if not len(matches_):
            return None

        return self._pools[self.get_key(**matches_.iloc[0])]

    def run(self):
        # Function possibly needs cleaning up, but should work for now
        # Setup event listening thread
        if not self._pools:
            return

        _pools = list(self._pools.values())
        address = [pool.address for pool in _pools]
        topics = [[_pools[0]._contract.events.__dict__[event].build_filter().event_topic
                   for event in self._pool_cls._events]]
        if not topics:
            return

        eth_filter = self.conn.create_filter(address=address, topics=topics)
        with ThreadPool(processes=self._processes) as pool:
            while not self._stop_event.is_set():
                pools_to_update = set(event['address'] for event in eth_filter.get_new_entries())
                pool.imap(func=lambda pool: pool.update(),
                          iterable=[self.get_pool_from_address(address=address) for address in pools_to_update])
                time.sleep(self._interval)

    def _load_address_book(self):
        address_book = BaseContract.load_csv(self._base_path, 'address_book', f'{self.conn}.csv')
        if address_book is None: address_book = pd.DataFrame(columns=self._address_book_columns)

        return address_book

    def _write_address_book(self):
        BaseContract.write_csv(self.address_book, self._base_path, 'address_book', f'{self.conn}.csv')

    @property
    def pools(self):
        return list(self._pools.values())

    @abc.abstractmethod
    def _get_pool(self, token_0, token_1, address=None):
        """
        Constructs and returns a pool instance, if it exists.

        :param token_0: Token0 Symbol
        :param token_1: Token1 Symbol
        :param address: (Optional) Pool address, will be looked-up on chain if not supplied.
        :return: BasePool or None
        """
        pass

    @abc.abstractmethod
    def update_pools(self):
        pass

    def get_pool(self, token_0, token_1):
        if (token_0, token_1) in self._pools:
            return self._pools[(token_0, token_1)]
        if (token_1, token_0) in self._pools:
            return self._pools[(token_1, token_0)]
        raise KeyError(f'Pool ({token_1}/{token_0}) not in {self}!')

    def add_address(self, address, **kwargs):
        """
        Writes address to the address book.

        :param address: address to be written to the book
        :param kwargs: dict of parameters to be included
        """
        if isinstance(kwargs['token_1'], BaseToken):
            kwargs['token_1'] = kwargs['token_1'].symbol
        if isinstance(kwargs['token_0'], BaseToken):
            kwargs['token_0'] = kwargs['token_0'].symbol

        n_index = len(self.address_book)
        check_value = self.address_book[(self.address_book['token_0'] == kwargs['token_0']) &
                                        (self.address_book['token_1'] == kwargs['token_1'])]
        if len(check_value):
            return

        self.address_book.loc[n_index] = dict(address=address, **kwargs)
        self._write_address_book()

    @classmethod
    def has_chain(cls, chain):
        if isinstance(chain, BaseChain):
            return chain.name in cls._config
        return chain in cls._config

    def __str__(self):
        return f'[{self.conn}] {self.__class__.__name__}'
