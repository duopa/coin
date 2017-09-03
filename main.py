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
    print("1 : EMA Cross with MACD")
    print("2 : MACD")
    '''
    print("101 : Macd-1min")
    print("103 : Macd-3min")
    print("105 : Macd-5min ")
    print("201 : EMA Cross with MACD-1min")
    print("203 : EMA Cross with MACD-3min")
    print("205 : EMA Cross with MACD-5min")
    '''
    strategy_selected = input(">>>")
    print("Please select time type:")
    print("1 : 1min")
    print("3 : 3min")
    print("5 : 5min")
    time_type = input(">>>")

    is_debug = input("Is debug? Y/N>>>")

    config = {}
    strategy = None
    frequency = 10
    if strategy_selected == "1":        
        if time_type == "1":
            frequency = 5
            time_type = "1min"
            config = eamcrosswithmacd_config_1min
        elif time_type == "3":
            time_type = "3min"
            config = eamcrosswithmacd_config_3min
        elif time_type == "5":
            time_type = "5min"
            config = eamcrosswithmacd_config_5min
        else:
            print("Invalid time type select {0}".format(time_type))
            return
        strategy = EmaCrossWithMacdStrategy(**config)
    elif strategy_selected == "2":        
        if time_type == "1":
            frequency = 5
            time_type = "1min"
            config = config_1min
        elif time_type == "3":
            time_type = "3min"
            config = config_3min
        elif time_type == "5":
            time_type = "5min"
            config = config_5min        
        else:
            print("Invalid time type select {0}".format(time_type))
            return
        strategy = MacdStrategy(**config)
    else:
        print("Invalid strategy selected {0}".format(strategy_selected))
        return    

    okcoin = OkCoin(symbol, time_type, frequency)
    okcoin.config = config
    strategy.symbol = symbol
    okcoin.strategy = strategy
    if str(is_debug).upper() == 'Y':
        okcoin.run_signal_test()
    else:
        okcoin.run()

if __name__ == "__main__":
    run()
