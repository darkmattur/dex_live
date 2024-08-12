from ..base import BaseWallet


class EthereumWallet(BaseWallet):
    def __init__(self, _conn, address, private_key=None, label='', **kwargs):
        super(EthereumWallet, self).__init__(_conn=_conn, label=label, address=address, private_key=private_key)

    def transaction_parameters(self, gas=10000000, gas_price=200000000):
        return {'nonce': self.transaction_count,
                'gas': gas,
                'gasPrice': gas_price,
                'chainId': self._conn.chain_id}
