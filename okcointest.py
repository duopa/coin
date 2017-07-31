from okcoin import *

'''
okcoin = OkCoin('eth_cny','3min', 175)
amount = okcoin._amount_to_buy(1234, 130)
print(amount)

okcoin = OkCoin('ltc_cny','3min', 175)
amount = okcoin._amount_to_buy(1234, 130)
print(amount)
'''


okcoin = OkCoin('eth_cny','3min', 175)
result = okcoin._is_reasonalbe_short_price(1366.46,1365, 1.008)
print(result)