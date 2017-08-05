from okcoin.OkCoin import OkCoin

stop_profit_loss_percents = [0.02, 0.02]
coin = OkCoin('eth_cny', '3min', 10, stop_profit_loss_percents)
coin.run()