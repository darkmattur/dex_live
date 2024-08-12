from .router import PancakeSwapV3Router

from ..uniswap_v3 import UniswapV3Edge


class PancakeSwapV3Edge(UniswapV3Edge):
    _router_cls = PancakeSwapV3Router
