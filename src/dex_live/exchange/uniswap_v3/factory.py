import pandas as pd
import itertools
from tqdm import tqdm

from .. import BaseFactory, BaseToken
from .pool import UniswapV3Pool


class UniswapV3(BaseFactory):
    _base_path = BaseFactory.clean_file_path(__file__)
    _config = BaseFactory.load_yml(__file__, 'config.yml')
    abi = BaseFactory.load_json(__file__, 'abi', 'factory.json')

    _address_book_columns = ['address', 'token_0', 'token_1', 'fee']
    _pool_cls = UniswapV3Pool
    _fee_tiers = [1, 5, 30, 100]  # Marked in Basis Points

    def __init__(self, chain):
        super(UniswapV3, self).__init__(chain)

    def get_key(self, token_0, token_1, fee, **kwargs):
        return token_0, token_1, fee

    def _get_pool(self, token_0, token_1, fee, address=None, **kwargs):
        """
        Constructs and returns a pool instance, if it exists.

        :param token_0: Token 0 Symbol
        :param token_1: Token 1 Symbol
        :param fee: Pool fee
        :param address: (Optional) Pool address, will be looked-up on chain if not supplied.
        :return: UniswapV3Pool or None
        """

        if address is None:
            token_0_address = self.conn.get_token_from_symbol(token_0).address
            token_1_address = self.conn.get_token_from_symbol(token_1).address

            address = self.functions.getPool(token_0_address, token_1_address, fee * 100)
            if address == self.ADDRESS_ZERO:
                return None

        return self._pool_cls(fee=fee, chain=self.conn, address=address, exchange=self)

    def get_pool(self, token_0, token_1, fee):
        if (token_0, token_1, fee) in self._pools:
            return self._pools[(token_0, token_1, fee)]
        if (token_1, token_0, fee) in self._pools:
            return self._pools[(token_1, token_0, fee)]
        raise KeyError(f'Pool ({token_1}/{token_0}) with fee "{fee}" not in {self.__class__.__name__}!')

    def add_address(self, address, **kwargs):
        if isinstance(kwargs['token_0'], BaseToken):
            kwargs['token_0'] = kwargs['token_0'].symbol
        if isinstance(kwargs['token_1'], BaseToken):
            kwargs['token_1'] = kwargs['token_1'].symbol

        check_value = self.address_book[(self.address_book['token_0'] == kwargs['token_0']) &
                                        (self.address_book['token_1'] == kwargs['token_1']) &
                                        (self.address_book['fee'] == kwargs['fee'])]
        if len(check_value):
            return

        self.address_book = pd.concat([
            self.address_book, pd.DataFrame([dict(address=address, **kwargs)])
        ], ignore_index=True)
        self._write_address_book()

    def update_pools(self):
        # Generate set of all known addresses
        k_token_0, k_token_1, k_fees = self.address_book['token_0'], self.address_book['token_1'], self.address_book['fee']
        known_pairs = {tuple(sorted([token_0, token_1]) + [fee]) for token_0, token_1, fee in
                       zip(k_token_0, k_token_1, k_fees)}

        # Generate set of all possible addresses
        all_pairs = [(token_0, token_1, fee) for (token_0, token_1), fee in
                     itertools.product(itertools.combinations(self.conn.tokens.keys(), r=2), self._fee_tiers)]

        for token_0, token_1, fee in tqdm(all_pairs,  desc=f'Updating pairs for {self.__class__.__name__}'):
            pair = tuple(sorted([token_0, token_1]) + [fee])
            if pair in known_pairs:
                continue

            pool = self._get_pool(token_0=token_0, token_1=token_1, fee=fee)
            # Connect to pool, sort keys into base/quote pairs.
            if pool is None:
                continue

            self.add_address(address=pool.address, token_0=pool.token_0, token_1=pool.token_1, fee=fee)
