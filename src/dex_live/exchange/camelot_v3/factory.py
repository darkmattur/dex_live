from .pool import CamelotV3Pool

from ..base import BaseFactory
from ..algebra_dex import AlgebraDEX


class CamelotV3(AlgebraDEX):
    _base_path = AlgebraDEX.clean_file_path(__file__)
    _config = BaseFactory.load_yml(__file__, 'config.yml')
    _pool_cls = CamelotV3Pool
