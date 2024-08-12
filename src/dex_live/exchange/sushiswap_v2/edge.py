from .router import SushiSwapV2Router

from ..uniswap_v2 import UniswapV2Edge


class SushiSwapV2Edge(UniswapV2Edge):
    _router_cls = SushiSwapV2Router
