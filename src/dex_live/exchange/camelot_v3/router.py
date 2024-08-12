from ..algebra_dex import AlgebraDexRouter


class CamelotV3Router(AlgebraDexRouter):
    _config = AlgebraDexRouter.load_yml(__file__, 'config.yml')
    router_index = 'router'
