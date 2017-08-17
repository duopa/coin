from okcoin.okcoin import OkCoin
from strategy import MacdStrategy, EmaCrossWithMacdStrategy
from okcoin.config import *

def run():
    print("please select symbol:")
    print("btc_cny: 1")
    print("eth_cny: 2")
    print("ltc_cny: 3")
    symbol_selected = input(">>>")

    symbol = "btc_cny"
    if symbol_selected == "1":
        symbol = "btc_cny"
    elif symbol_selected == "2":
        symbol = "eth_cny"
    elif symbol_selected == "3":
        symbol = "ltc_cny"
    else:
        print("Invalid symbol selected {0}".format(symbol_selected))
        return

    print("please select strategy:")
    print("103 : Macd-3min")
    print("105 : Macd-5min ")
    print("203 : EMA Cross with MACD-3min")
    print("205 : EMA Cross with MACD-5min")
    strategy_selected = input(">>>")

    config = {}
    time_type = "3min"
    strategy = None
    if strategy_selected == "103":
        time_type = "3min"
        config = config_3min
        strategy = MacdStrategy(**config)
    elif strategy_selected == "105":
        time_type = "5min"
        config = config_5min
        strategy = MacdStrategy(**config)
    elif strategy_selected == "203":
        time_type = "3min"
        config = eamcrosswithmacd_config_3min
        strategy = EmaCrossWithMacdStrategy(**config)
    elif strategy_selected == "205":
        time_type = "5min"
        config = eamcrosswithmacd_config_5min
        strategy = EmaCrossWithMacdStrategy(**config)
    else:
        print("Invalid strategy selected {0}".format(strategy_selected))
        return

    okcoin = OkCoin(symbol, time_type, 10)
    okcoin.config = config
    okcoin.strategy = strategy
    okcoin.run()

if __name__ == "__main__":
    run()
