from okcoin.OkCoin import OkCoin

stop_profit_loss_percents = [0.015, 0.02]
coin = OkCoin('ltc_cny', '3min', 10, stop_profit_loss_percents)
coin.run()