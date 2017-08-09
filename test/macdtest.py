import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir)))
from strategy import MacdStrategy
from okcoin.OkcoinSpotAPI import OKCoinSpot
from okcoin.key import *
from okcoin.config import *


#初始化apikey，secretkey,url
apikey = api_key
secretkey = secret_key
okcoinRESTURL = url_cn
okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)
macd = MacdStrategy()

'''
ticker = '{"date":"1410431279","ticker":{ "buy":"33.15","high":"34.15","last":"33.15","low":"32.05","sell":"33.16","vol":"10532696.39199642"}}'
def test_should_stop_loss_shoud_return_true():
    result = macd.should_stop_loss(json.loads(ticker), 34)
    if result == True:
        print('test_should_stop_loss_shoud_return_true pass')
    else:
        print('test_should_stop_loss_shoud_return_true failed')

def test_should_stop_loss_shoud_return_false():
    result = macd.should_stop_loss(json.loads(ticker), 33)
    if result == False:
        print('test_should_stop_loss_shoud_return_false pass')
    else:
        print('test_should_stop_loss_shoud_return_false failed')

test_should_stop_loss_shoud_return_true()
test_should_stop_loss_shoud_return_false()

date = int(json.loads(ticker)['date'])
print(date)
'''

#-----------------------------------------------------------------------------------------------------------------------
def _is_dif_negtive_when_hist_changeing_to_negtive_should_return_true():
    result = macd._is_dif_negtive_when_hist_changeing_to_negtive([1, 2, -3, -4, -5, -6, -7], [1, 2, 3, -1, -2, -3, -4])
    if result:
        print('_is_dif_negtive_when_hist_changeing_to_negtive_should_return_true PASS')
    else:
        print('_is_dif_negtive_when_hist_changeing_to_negtive_should_return_true FAILED')

def _is_dif_negtive_when_hist_changeing_to_negtive_should_return_false():
    result = macd._is_dif_negtive_when_hist_changeing_to_negtive([1, 2, 3, 4, -5, -6, -7], [1, 2, 3, -1, -2, -3, -4])
    if not result:
        print('_is_dif_negtive_when_hist_changeing_to_negtive_should_return_false PASS')
    else:
        print('_is_dif_negtive_when_hist_changeing_to_negtive_should_return_false FAILED')

_is_dif_negtive_when_hist_changeing_to_negtive_should_return_true()
_is_dif_negtive_when_hist_changeing_to_negtive_should_return_false()
#-----------------------------------------------------------------------------------------------------------------------

def test_is_dif_above_dea_back_n_periods_should_return_true():
    result = macd._is_dif_above_dea_back_n_periods([0.1, -0.2, 0.3, 0.4], [0.2, -0.4, 0, 0.1], 3)
    if result == True:
        print('test_is_dif_above_dea_back_n_periods_should_return_true pass')
    else:
        print('test_is_dif_above_dea_back_n_periods_should_return_true failed')

def test_is_dif_above_dea_back_n_periods_should_return_false():
    result = macd._is_dif_above_dea_back_n_periods([0.2, -0.4, 0, 0.5], [0.1, -0.2, 0.3, 0.4], 3)
    if result == False:
        print('test_is_dif_above_dea_back_n_periods_should_return_true pass')
    else:
        print('test_is_dif_above_dea_back_n_periods_should_return_true failed')

test_is_dif_above_dea_back_n_periods_should_return_true()
test_is_dif_above_dea_back_n_periods_should_return_false()    
#------------------------------------------------------------------------------------------------------------------
def test_is_pre_dif_dea_far_enough_should_return_false():
    result = macd._is_pre_dif_dea_far_enough([-3.23,-2.81,-3.09,-3.0], [-4.00,-3.76,-3.62,-3.5])
    if not result:
        print('test_is_pre_dif_dea_far_enough_should_return_false PASS')
    else:
        print('test_is_pre_dif_dea_far_enough_should_return_false FAILED')

test_is_pre_dif_dea_far_enough_should_return_false()

#------------------------------------------------------------------------------------------------------------------
def test_is_long_price_under_highest_price_percent_should_return_false():
    kline = okcoinSpot.kline('eth_cny', '3min', 130)
    result = macd._is_long_price_under_highest_price_percent(kline,22704)
    if not result:
        print('test_is_long_price_under_highest_price_percent_should_return_false PASS')
    else:
        print('test_is_long_price_under_highest_price_percent_should_return_false FAILED<<<------')

def test_is_long_price_under_highest_price_percent_should_return_true():
    kline = okcoinSpot.kline('btc_cny', '5min', 130)
    result = macd._is_long_price_under_highest_price_percent(kline,22704)
    if result:
        print('test_is_long_price_under_highest_price_percent_should_return_true PASS')
    else:
        print('test_is_long_price_under_highest_price_percent_should_return_true FAILED<<<------')

test_is_long_price_under_highest_price_percent_should_return_true()
test_is_long_price_under_highest_price_percent_should_return_false()
#-------------------------------------------------------------------------------------------------------------------
def test_price_vibrate_rate():
    kline = okcoinSpot.kline('btc_cny', '3min', 130)
    result = macd._get_price_vibrate_rate(kline)
    print('price_vibrate_rate:{0}'.format(result))

test_price_vibrate_rate()
#-----------

kline =[
    [
        1417536000000,
        2370.16,
        2180,
        2352,
        2367.37,
        17259.83
    ],
    [
        1417449600000,
        2339.11,
        2383.15,
        2322,
        2369.85,
        83850.06
    ],
    [
        1417536000000,
        2370.16,
        2380,
        2352,
        2367.37,
        17259.83
    ]
]
def test_get_highest_price():
    highest_price = macd._get_highest_price_from_kline(kline)
    if highest_price == 2383.15:
        print('test_get_highest_price PASS')
    else:
        print('test_get_highest_price FAILED<<<---')

test_get_highest_price()