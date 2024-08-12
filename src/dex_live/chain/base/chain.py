import web3
import re

from dex_live import config

import abc
import itertools
from collections import defaultdict

import threading
from multiprocessing.pool import ThreadPool
import time

from hexbytes import HexBytes

from .. import construct_chain_tokens, BaseToken
from .wallet import BaseWallet


class BaseChain(threading.Thread, abc.ABC):
    daemon = True
    _interval = 0.5
    _processes = 8

    @property
    @abc.abstractmethod
    def name(self):
        pass

    @property
    @abc.abstractmethod
    def _conn(self) -> web3.Web3:
        pass

    @property
    def tokens(self):
        return self._tokens

    @classmethod
    def _get_conn(cls, url, **kwargs):
        if re.match(r'http(s)?:.+', url):
            provider = web3.HTTPProvider(url, **kwargs)
        elif re.match(r'wss:.+', url):
            provider = web3.WebsocketProvider(url, **kwargs)
        else:
            raise ValueError(f'Unable to recognise provider for "{url}"')

        return web3.Web3(provider)

    def __init__(self):
        super(BaseChain, self).__init__()
        self._contracts = []
        self._stop_event = threading.Event()

        self._tokens = construct_chain_tokens(chain=self.name, conn=self)
        self._token_from_address = {token.address: token for token in self._tokens.values()}

        self._wallets = dict()
        for wallet_name, wallet_config in config[self.name].get('wallets', {}).items():
            self._wallets[wallet_name] = self._wallet_cls(_conn=self, label=wallet_name, **wallet_config)

        self._wallet_from_address = {wallet.address: wallet for wallet in self._wallets.values()}

        self.start()

    def run(self):
        if not self._wallets:
            return

        token_addresses = [token.address for token in self._tokens.values()]
        if not token_addresses:
            return

        token_events = list(set(itertools.chain(*[token.events for token in self._tokens.values()])))
        if not token_events:
            return

        wallet_addresses = [f"{int(address, 16):#066x}" for address in self._wallet_from_address.keys()]
        if not wallet_addresses:
            return

        receive_filter = self.create_filter(address=token_addresses, topics=[token_events, None, wallet_addresses])
        send_filter = self.create_filter(address=token_addresses, topics=[token_events, wallet_addresses, None])

        with ThreadPool(processes=self._processes) as pool:
            while not self._stop_event.is_set():
                # Build filters
                wallet_update = defaultdict(set)
                for event in receive_filter.get_new_entries():
                    _, sender, receiver = event['topics']
                    wallet_update[receiver].add(event['address'])

                for event in send_filter.get_new_entries():
                    _, sender, receiver = event['topics']
                    wallet_update[sender].add(event['address'])

                def _update_wallet(address, tokens):
                    if (wallet := self.get_wallet(address)) is not None:
                        wallet.update(tokens=tokens)

                pool.starmap(func=_update_wallet, iterable=wallet_update.items())
                time.sleep(self._interval)

    def get_token_from_address(self, address):
        """
        Parameters
        ----------
        first : string
            token address

        Returns
        -------
        token_object
            returns token object
        """

        if address not in self._token_from_address:
            raise ValueError(f'Unable to find token with address "{address}" on chain "{self.__class__.__name__}"!')
        return self._token_from_address[address]

    def get_token_from_symbol(self, symbol):
        """
        Parameters
        ----------
        first : string
            symbol

        Returns
        -------
        token_object
            returns token object
        """
        if symbol not in self._tokens:
            raise ValueError(f'Unable to find token with symbol "{symbol}" on chain "{self.__class__.__name__}"!')
        return self._tokens[symbol]

    def get_token(self, token):
        if isinstance(token, HexBytes):
            token = f'0x{token.hex()[2:].rjust(20, "0")}'
        elif isinstance(token, bytes):
            token = f'0x{token.hex().rjust(20, "0")}'

        if isinstance(token, BaseToken):
            return token

        if token in self._tokens:
            return self._tokens[token]
        if token in self._token_from_address:
            return self._token_from_address[token]

    def get_wallet(self, wallet):
        if isinstance(wallet, bytes):
            # Messy but how else can you cover translating byte address input to the format we store it in?
            wallet = web3.Web3.to_checksum_address(f'0x{wallet.hex()[-40:].rjust(40, "0")}')

        if isinstance(wallet, BaseWallet):
            return wallet

        if wallet in self._wallets:
            return self._wallets[wallet]
        if wallet in self._wallet_from_address:
            return self._wallet_from_address[wallet]

    def create_contract(self, address, abi):
        return self._conn.eth.contract(address=address, abi=abi)

    def create_filter(self, address, **kwargs):
        return self._conn.eth.filter(dict(address=address, fromBlock='latest', **kwargs))

    def send_transaction(self, transaction, private_key):
        signed_transaction = self._conn.eth.account.sign_transaction(
            transaction_dict=transaction, private_key=private_key)

        tx_hash = self._conn.eth.send_raw_transaction(signed_transaction.rawTransaction)
        tx_receipt = self._conn.eth.wait_for_transaction_receipt(tx_hash)

        return tx_receipt

    def get_transaction_count(self, address):
        return self._conn.eth.get_transaction_count(address)

    @property
    @abc.abstractmethod
    def _wallet_cls(self) -> type:
        pass

    def __repr__(self):
        return self.name
