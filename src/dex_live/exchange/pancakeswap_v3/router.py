from ..uniswap_v3 import UniswapV3Router


class PancakeSwapV3Router(UniswapV3Router):
    abi = UniswapV3Router.load_json(__file__, 'abi', 'router.json')
    _config = UniswapV3Router.load_yml(__file__, 'config.yml')
    router_index = 'router_3'
