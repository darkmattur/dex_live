from .router import CamelotV3Router

from ..algebra_dex import AlgebraDexEdge


class CamelotV3Edge(AlgebraDexEdge):
    _router_cls = CamelotV3Router
