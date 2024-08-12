from .edge import CamelotV2Edge

from ..uniswap_v2 import UniswapV2Pair


class CamelotV2Pair(UniswapV2Pair):
    _base_path = UniswapV2Pair.clean_file_path(__file__)
    abi = UniswapV2Pair.load_json(__file__, 'abi', 'pair.json')
    _events = ['Mint', 'Swap', 'Burn', 'Sync']
    fee = None
    _edge_cls = CamelotV2Edge

    def __init__(self, chain, address, exchange, token_0=None, token_1=None):
        super(CamelotV2Pair, self). __init__(
            chain=chain, address=address, exchange=exchange, token_0=token_0, token_1=token_1)
        self.token_1_fee, self.token_0_fee = None, None

    # For some fucking reason, CamelotV2 measures its fees in 1/10th of a basis point.
    def _token_1_fee(self):
        return self.functions.token1FeePercent() / 10

    def _token_0_fee(self):
        return self.functions.token0FeePercent() / 10

    def update(self):
        self.token_1_fee, self.token_0_fee = self._token_1_fee(), self._token_0_fee()
        super(CamelotV2Pair, self).update()
