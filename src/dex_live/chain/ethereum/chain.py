from dex_live import config

from ..base import BaseChain
from .wallet import EthereumWallet

ethereum_config = config.get('ethereum')


class Ethereum(BaseChain):
    name = 'ethereum'
    chain_id = 1
    _wallet_cls = EthereumWallet

    if ethereum_config:
        _conn = BaseChain._get_conn(ethereum_config['url'])

    def __init__(self):
        if not self._conn:
            raise EnvironmentError(f'No config for {self.__class__.__name__} provided!')
        super(Ethereum, self).__init__()
