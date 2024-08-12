from ..uniswap_v3 import UniswapV3
from .pool import PancakeSwapV3Pool


class PancakeSwapV3(UniswapV3):
    _base_path = UniswapV3.clean_file_path(__file__)
    _config = UniswapV3.load_yml(__file__, 'config.yml')
    abi = UniswapV3.load_json(__file__, 'abi', 'factory.json')

    _pool_cls = PancakeSwapV3Pool
    _fee_tiers = [1, 5, 25, 100]
