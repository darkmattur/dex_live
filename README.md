# dex_live
## a Python DeFi trading suite

created as a part of the MSc Risk Management & Financial Engineering course from Imperial College Business School

### Installation

The module can be installed using the command `pip install -e /path/to/dex_live`.

### Configuration

The module requires a configuration folder to be set up, with the chain access details, as well as securely storing sensitive information such as wallet addresses and private keys. The configuration folder should contain a `.yml` file for each chain required:

```bash
/path/to/dex_live_config
├── ethereum.yml
├── arbitrum.yml
├── ...
```

Currently, the module is only equipped to access Ethereum and Arbitrum. However, due to its modular nature, it can be easily extended to other Layer 2 networks, as well as other non-Ethereum-based networks that support web3 RPC. Each configuration file should have the following structure:

```yaml
url: "https://web3_rpc_url/"

wallets:
    <wallet_01>:
        address: "<wallet_01_address>"
        public_key: "<wallet_01_public_key>"
        private_key: "<wallet_01_private_key>"
        
    <wallet_02>: ...
```

The util folder contains a .ipynb notebook that can be used to generate wallet addresses and public/private key pairs, which can then be included inside the configuration files. Including wallets is optional if the module is used only to view the current state of the chain, but required for trading.

The path to the configuration folder should be set as an environment variable under the name `CRYPTO`. After this is done, the module can be imported into a script via import dex_live. To check the configuration functions correctly, a script to read the balance of a given token can be run using:

```python
from dex_live.chain import ChainManager

chain_name = 'eth'
wallet_name = 'wallet_01'
token_name = 'USDT'

chain = ChainManager.get_chain(chain_name)
wallet = chain.get_wallet(wallet_name)

print(wallet.balance[token_name])
```
