from functools import lru_cache

from .base import BaseChain

from .ethereum import Ethereum
from .arbitrum import ArbitrumOne


class ChainManager:
    def __init__(self):
        pass

    @staticmethod
    def get_chain(name):
        if isinstance(name, BaseChain):
            return name
        return ChainManager._get_chain(name)

    @staticmethod
    @lru_cache(maxsize=None)
    def _get_chain(name):
        match name.lower():
            case 'eth' | 'ethereum' | 'mainnet':
                return Ethereum()
            case 'arb' | 'arbitrum' | 'arbitrumone' | 'arbitrum_one':
                return ArbitrumOne()
            case _:
                raise ValueError(f'Unable to find chain "{name}"!')
