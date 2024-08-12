from .edge import PancakeSwapV3Edge

from ..uniswap_v3 import UniswapV3Pool


class PancakeSwapV3Pool(UniswapV3Pool):
    _base_path = UniswapV3Pool.clean_file_path(__file__)
    abi = UniswapV3Pool.load_json(__file__, 'abi', 'pool.json')
    _edge_cls = PancakeSwapV3Edge
