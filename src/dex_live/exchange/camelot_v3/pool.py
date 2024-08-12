from .edge import CamelotV3Edge

from ..algebra_dex import AlgebraDEXPool


class CamelotV3Pool(AlgebraDEXPool):
    _base_path = AlgebraDEXPool.clean_file_path(__file__)
    _edge_cls = CamelotV3Edge
