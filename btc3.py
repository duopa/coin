from okcoin.OkCoin import *

stop_profit_loss_percents = [0.02, 0.03]
okcoin = OkCoin('btc_cny', '3min', 10, stop_profit_loss_percents)
okcoin.run()