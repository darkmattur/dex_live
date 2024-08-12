from ..uniswap_v2 import UniswapV2
from .pool import SushiSwapV2Pair


class SushiSwapV2(UniswapV2):
    _base_path = UniswapV2.clean_file_path(__file__)
    _config = UniswapV2.load_yml(__file__, 'config.yml')
    _pool_cls = SushiSwapV2Pair
