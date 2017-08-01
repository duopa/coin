from okcoin import *

'''
okcoin = OkCoin('eth_cny','3min', 175)
amount = okcoin._amount_to_buy(1234, 130)
print(amount)

okcoin = OkCoin('ltc_cny','3min', 175)
amount = okcoin._amount_to_buy(1234, 130)
print(amount)
'''


okcoin = OkCoin('btc_cny','3min', 175)
avg_price = okcoin._get_last_n_long_avg_price(2, 5)
if okcoin._is_reasonalbe_short_price(19238.0, avg_price, 1.008):
    print('short')
else:
    print(avg_price)