import abc


class BaseEdge(abc.ABC):
    def __init__(self, pool, token_in, token_out):
        self.pool = pool
        self.token_in, self.token_out = token_in, token_out
        self.swap_address = self.pool.address

        self.long = (self.pool.token_1, self.pool.token_0) == (self.token_out, self.token_in)

    @property
    def rate(self):
        if self.pool.rate is None:
            return None

        if self.long:
            return (10000 - self.pool.fee) * self.pool.rate / 10000
        else:
            return (10000 - self.pool.fee) / (self.pool.rate * 10000)

    @property
    def raw(self):
        return self.pool.rate if self.long else (1.0 / self.pool.rate)

    @property
    def exchange(self):
        return self.pool.exchange

    def preapprove(self, wallet):
        if self.token_in.check_approved_spend(wallet, self.swap_address) < 1_000_000:
            self.token_in.approve_spend(wallet, self.swap_address)

    @abc.abstractmethod
    def swap(self, wallet, amount, max_slippage=100.0, **kwargs):
        pass

    def __repr__(self):
        return f'[{self.pool.conn.name}] {self.__class__.__name__} ({self.token_in.symbol}/{self.token_out.symbol})'
