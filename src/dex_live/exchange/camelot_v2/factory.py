from ..uniswap_v2 import UniswapV2
from .pool import CamelotV2Pair


class CamelotV2(UniswapV2):
    _base_path = UniswapV2.clean_file_path(__file__)
    _config = UniswapV2.load_yml(__file__, 'config.yml')
    abi = UniswapV2.load_json(__file__, 'abi', 'factory.json')
    _pool_cls = CamelotV2Pair
