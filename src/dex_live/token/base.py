import abc

from ..base import BaseContract


class BaseToken(BaseContract):
    def __init__(self, symbol, name, decimals, chain, address):
        super(BaseToken, self).__init__(chain=chain, address=address)
        self.symbol, self.name = symbol, name
        self.decimals = decimals

    def __repr__(self):
        return f'[{self.conn}] {self.symbol} ({self.__class__.__name__})'

    def update(self):
        pass

    @property
    @abc.abstractmethod
    def events(self):
        """
        Returns the topics for each event for which the balance of a wallet changes

        """
        pass

    @abc.abstractmethod
    def get_balance(self, address):
        """
        Returns the balance of the specified token for the specified wallet

        :param address: address of the wallet to be checked
        :type address: str
        :returns: current balance
        :rtype: float
        """
        pass

    @abc.abstractmethod
    def check_approved_spend(self, wallet, address):
        pass

    @abc.abstractmethod
    def approve_spend(self, wallet, address, amount=None):
        pass

    def token_to_decimals(self, amount) -> int:
        return int(amount * pow(10.0, self.decimals))

    def decimals_to_token(self, amount) -> float:
        return amount / pow(10.0, self.decimals)

    def __eq__(self, other):
        if isinstance(other, str):
            return (self.symbol == other) or (self.address == other)
        if isinstance(other, BaseToken):
            return (self.conn.name, self.symbol) == (other.conn.name, other.symbol)
