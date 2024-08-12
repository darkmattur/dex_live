from ..uniswap_v2 import UniswapV2Router


class SushiSwapV2Router(UniswapV2Router):
    _config = UniswapV2Router.load_yml(__file__, 'config.yml')
    router_index = 'router_2'
