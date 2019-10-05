# provide-python

Provide python client library.

## Installation

`pip install prvd`

## pipenv

`pipenv install` uses the Pipefile to install package dependencies.

## Usage

Basic transaction creation using a Provide API token:

```python
from prvd.goldmine import Goldmine

client = Goldmine('your-provide-application-api-token')
params = { 'wallet_id': 'your-provide-application-wallet-uuid', 'method': 'delegate', 'value': 0, 'params': ["0x3109F8317aef2959dA5F57973031B9B43c0c617d"] }
client.execute_contract('your-provide-application-smart-contract-uuid', params)
```
