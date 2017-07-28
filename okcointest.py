from okcoin import *

okcoin = OkCoin('eth_cny','3min', 175)
amount = okcoin._amount_to_buy(1234, 130)
print(amount)

okcoin = OkCoin('ltc_cny','3min', 175)
amount = okcoin._amount_to_buy(1234, 130)
print(amount)