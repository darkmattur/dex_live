from ..base import BaseContract

from .base import BaseToken
from .erc20.contract import ERC20Token

tokens = BaseContract.load_yml(__file__, 'tokens.yml')


def construct_chain_tokens(chain, conn):
    chain_tokens = dict()
    for symbol, config in tokens.items():
        if chain not in config['address']:
            continue

        address = config['address'][chain]
        match config['abi'].lower():
            case 'erc20':
                token_instance = ERC20Token(symbol=symbol,
                                            name=config['name'],
                                            decimals=config['decimals'],
                                            chain=conn, address=address)
            case _:
                raise ValueError(f'Token ABI {config["abi"]} not recognised!')

        chain_tokens[symbol] = token_instance

    return chain_tokens
