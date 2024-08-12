from ..base import BaseToken


class ERC20Token(BaseToken):
    abi = BaseToken.load_json(__file__, 'abi.json')

    unlimited_approval_amount = int('ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff', 16)

    def __init__(self, symbol, name, decimals, chain, address):
        super(ERC20Token, self).__init__(symbol=symbol, name=name, decimals=decimals,
                                         chain=chain, address=address)

    @property
    def events(self):
        return [self._contract.events.__dict__[event].build_filter().event_topic
                for event in ['Transfer', 'Approval']]

    def check_approved_spend(self, wallet, address):
        return self.functions.allowance(wallet.address, address)

    def approve_spend(self, wallet, address, amount=None):
        if amount is not None:
            amount = self.token_to_decimals(amount)
        else:
            amount = self.unlimited_approval_amount

        return wallet.execute(
            self._contract.functions.approve(address, amount)
        )

    def get_balance(self, address):
        return self.functions.balanceOf(address)
