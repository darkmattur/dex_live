from . import UniswapV2, CamelotV2, SushiSwapV2
from . import CamelotV3
from . import UniswapV3, PancakeSwapV3


class ExchangeManager:
    _contracts = [
        UniswapV2, CamelotV2, SushiSwapV2,  # UniV2 forks
        CamelotV3,  # AlgebraDex forks
        UniswapV3, PancakeSwapV3  # UniV3 forks
    ]

    def __init__(self, chain, exchanges=None):
        self.factories = dict()

        contract_cls_list = self._contracts
        if exchanges:
            exchange_set = set(exchanges)
            contract_cls_list = [
                contract_cls for contract_cls in contract_cls_list
                if contract_cls.__name__ in exchange_set
            ]

        for contract_cls in contract_cls_list:
            if contract_cls.has_chain(chain):
                self.factories[contract_cls.__name__] = contract_cls(chain=chain)

        self.pools = sum([factory.pools for factory in self.factories.values()], [])
        self.edges = sum([factory.edges for factory in self.factories.values()], [])

    # TODO: Expand this interface, add nice method for accessing pools/edges
