import abc
from hexbytes import HexBytes

from tqdm import tqdm
from multiprocessing.pool import ThreadPool

from ..base import BaseToken


class WalletMeta(abc.ABCMeta):
    """
    Metaclass to handle post initialisation tasks
    """
    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        instance.__post_init__()
        return instance


class BaseWallet(metaclass=WalletMeta):
    _multithread_thresh = 8
    _processes = 8

    class _balance_cls(dict):
        __getattr__ = dict.get

    @property
    def transaction_count(self):
        return self._conn.get_transaction_count(self.address)

    @abc.abstractmethod
    def transaction_parameters(self):
        pass

    def __init__(self, _conn, address, private_key=None, label=''):
        self._conn = _conn

        self.label, self.address = label, address

        self.private_key = None
        if private_key is not None:
            self.private_key = HexBytes(private_key)

        self.balance = self._balance_cls()

    def __post_init__(self):
        self.update(verbose=True)

    def update(self, tokens=None, verbose=False):
        # Standardise inputs
        if tokens is None:
            tokens = self._conn.tokens.keys()
        if isinstance(tokens, (str, BaseToken)):
            tokens = [tokens]
        if not isinstance(tokens, (list, set)):
            tokens = list(tokens)

        # Ensure all values in list are tokens
        tokens_ = []
        for token_ in tokens:
            if (c_token := self._conn.get_token(token_)) is not None:
                tokens_.append(c_token)

        with ThreadPool(processes=min(self._processes, len(tokens_))) as pool:
            mp_update = pool.imap(func=lambda token: (token.symbol, token.get_balance(self.address)), iterable=tokens_)
            if verbose:
                mp_update = tqdm(iterable=mp_update,
                                 desc=f'Initialising balances for {self}',
                                 total=len(tokens_))

                self.balance.update(list(mp_update))

    def execute(self, transaction, **kwargs):
        if self.private_key is None:
            raise ValueError(f'Unable to sign transactions for read-only wallet {self}!')

        return self._conn.send_transaction(
            transaction.build_transaction(self.transaction_parameters()),
            self.private_key
        )

    def __repr__(self):
        return f'[{self._conn}] {self.label}'
