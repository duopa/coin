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
avg_price = okcoin._get_last_n_long_avg_price(2, 10)
print(avg_price)
'''
if okcoin._is_reasonalbe_short_price(1508.53, avg_price, 1.008):
    print('short')
else:
    print(avg_price)
'''

'''
okcoin._update_user_info()
amount = okcoin._amount_to_long(287)
print(amount)
'''