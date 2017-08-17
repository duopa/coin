import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir)))
from strategy import EmaCrossWithMacdStrategy
from okcoin.OkcoinSpotAPI import OKCoinSpot
from okcoin.key import *
from okcoin.config import *


#初始化apikey，secretkey,url
apikey = api_key
secretkey = secret_key
okcoinRESTURL = url_cn
okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)
strategy = EmaCrossWithMacdStrategy(**eamcrosswithmacd_config_3min)


_ticker = okcoinSpot.ticker('eth_cny')
ticker = _ticker['ticker']
last = float(ticker['last'])
long_price = float(ticker['buy'])
short_price = float(ticker['sell'])
avg_long_price = 2000
holding = 0 #float(self._funds['free'][self._coin_name])

kwargs = {'last': last, 'long_price': long_price, 'short_price': short_price, 'avg_long_price': avg_long_price, 'holding':holding}

kline = okcoinSpot.kline('eth_cny', '3min', 130)
strategy.execute(kline, **kwargs)

def test_is_ema_golden_cross():
    result = strategy._is_ema_golden_cross()
    print(result)

def test_is_ema_dead_cross():
    result = strategy._is_ema_dead_cross()
    print(result)

def test_is_on_ranging():
    result = strategy._is_on_ranging()
    print(result)


test_is_ema_golden_cross()
test_is_ema_dead_cross()
test_is_on_ranging()