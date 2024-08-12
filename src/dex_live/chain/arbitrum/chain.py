from dex_live import config

from ..base import BaseChain
from ..ethereum import EthereumWallet

arbitrum_config = config['arbitrum']


class ArbitrumOne(BaseChain):
    name = 'arbitrum'
    chain_id = 42161
    _wallet_cls = EthereumWallet

    _conn = BaseChain._get_conn(arbitrum_config['url'])

    def __init__(self):
        if not self._conn:
            raise EnvironmentError(f'No config for {self.__class__.__name__} provided!')
        super(ArbitrumOne, self).__init__()
