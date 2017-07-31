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