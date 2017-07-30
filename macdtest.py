import sys
import os
import json
from strategy import *

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
    result = macd._is_dif_negtive_when_hist_changeing_to_negtive([1, 2, 3, -4, -5, -6, -7], [1, 2, 3, -1, -2, -3, -4])
    if result:
        print('_is_dif_negtive_when_hist_changeing_to_negtive_should_return_true PASS')
    else:
        print('_is_dif_negtive_when_hist_changeing_to_negtive_should_return_true FAILED')

def _is_dif_negtive_when_hist_changeing_to_negtive_should_return_false():
    result = macd._is_dif_negtive_when_hist_changeing_to_negtive([1, 2, 3, 4, -5, -6, -7], [1, 2, 3, -1, -2, -3, -4])
    if not result:
        print('_is_dif_negtive_when_hist_changeing_to_negtive_should_return_true PASS')
    else:
        print('_is_dif_negtive_when_hist_changeing_to_negtive_should_return_true FAILED')

_is_dif_negtive_when_hist_changeing_to_negtive_should_return_true()
_is_dif_negtive_when_hist_changeing_to_negtive_should_return_false()
#-----------------------------------------------------------------------------------------------------------------------