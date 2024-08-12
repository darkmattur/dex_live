import pandas as pd
import itertools
from tqdm import tqdm

from ..base import BaseFactory
from .pool import UniswapV2Pair


class UniswapV2(BaseFactory):
    _base_path = BaseFactory.clean_file_path(__file__)
    _config = BaseFactory.load_yml(__file__, 'config.yml')
    abi = BaseFactory.load_json(__file__, 'abi', 'factory.json')
    _pool_cls = UniswapV2Pair

    def __init__(self, chain):
        super(UniswapV2, self).__init__(chain=chain)

    def _get_pool(self, token_0, token_1, address=None, **kwargs):
        """
        Constructs and returns a pool instance, if it exists.

        :param token_0: Token 0 Symbol
        :param token_1: Token 1 Symbol
        :param fee: Pool fee
        :param address: (Optional) Pool address, will be looked-up on chain if not supplied.
        :return: UniswapV2Pool or None
        """

        if address is None:
            token_0_address = self.conn.get_token_from_symbol(token_0).address
            token_1_address = self.conn.get_token_from_symbol(token_1).address

            address = self.functions.getPair(token_0_address, token_1_address)
            if address == self.ADDRESS_ZERO:
                return None

        return self._pool_cls(chain=self.conn, address=address, exchange=self)

    def update_pools(self):
        # Generate set of all known addresses
        k_token_1, k_token_0 = self.address_book['token_1'], self.address_book['token_0']
        known_pairs = {tuple(sorted([token_1, token_0])) for token_1, token_0 in zip(k_token_1, k_token_0)}

        # Generate set of all possible addresses
        all_pairs = list(itertools.combinations(self.conn.tokens.keys(), r=2))

        for token_0, token_1 in tqdm(all_pairs,  desc=f'Updating pairs for {self}'):
            pair = tuple(sorted([token_0, token_1]))
            if pair in known_pairs:
                continue

            pool = self._get_pool(token_0, token_1)
            # Connect to pool, sort keys into base/quote pairs.
            if pool is None:
                continue

            self.add_address(address=pool.address, token_1=pool.token_1, token_0=pool.token_0)
