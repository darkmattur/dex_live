from .edge import SushiSwapV2Edge

from ..uniswap_v2 import UniswapV2Pair


class SushiSwapV2Pair(UniswapV2Pair):
    _base_path = UniswapV2Pair.clean_file_path(__file__)
    _edge_cls = SushiSwapV2Edge
