
import sys
import os
import sys
import os
#sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir)))
from strategy import MacdStrategy

macd = MacdStrategy()
##################################################################
def test_is_slope_changing_to_positive_should_return_true():
    result = macd._is_slope_changing_to_positive([0, 1.2, -1.0, 0.1, 0.2])
    if result == True:
        print('test_is_slope_changing_to_positive_should_return_true pass')
    else:
        print('test_is_slope_changing_to_positive_should_return_true failed')

def test_is_slope_changing_to_positive_should_return_false():
    result = macd._is_slope_changing_to_positive([0, 1, -1.0, 0.2, 0.1])
    if result == False:
        print('test_is_slope_changing_to_positive_should_return_false pass')
    else:
        print('test_is_slope_changing_to_positive_should_return_false failed')
##################################################################
def test_long_signal_should_return_true():
    result = macd._long_signal([0, 1.2, -1.0, -0.2, -0.2], [-1])
    if result == True:
        print('test_long_signal_should_return_true pass')
    else:
        print('test_long_signal_should_return_true failed')

#false becuase last two are positive numbers
def test_long_signal_should_return_false():
    result = macd._long_signal([0, 1.2, -1.0, 0.2, 0.2], [1])
    if result == False:
        print('test_long_signal_should_return_false pass')
    else:
        print('test_long_signal_should_return_false failed')

##################################################################
def test_short_signal_should_return_true():
    result = macd._short_signal([0, -2.1, -2.0, -0.2, -0.3], [])
    if result == True:
        print('test_short_signal_should_return_true pass')
    else:
        print('test_short_signal_should_return_true failed')

def test_short_signal_should_return_false():
    result = macd._short_signal([0, -1.9, -2.0, -0.2, -0.1], [])
    if result == False:
        print('test_short_signal_should_return_false pass')
    else:
        print('test_short_signal_should_return_false failed')

##################################################################


def test_is_dif_under_dea_back_n_periods_should_return_true():
    result = macd._is_dif_under_dea_back_n_periods([0.2, -0.4, 0, 0.1],[0.1, -0.2, 0.3, 0.4], 3)
    if result == True:
        print('test_is_dif_under_dea_back_n_periods_should_return_true pass')
    else:
        print('test_is_dif_under_dea_back_n_periods_should_return_true failed')

def test_is_dif_under_dea_back_n_periods_should_return_false():
    result = macd._is_dif_under_dea_back_n_periods([0.1, -0.2, 0.3, 0.4], [0.2, -0.4, 0, 0.1], 3)
    if result == False:
        print('test_is_dif_under_dea_back_n_periods_should_return_true pass')
    else:
        print('test_is_dif_under_dea_back_n_periods_should_return_true failed')


ticker = '{"date":"1410431279","ticker":{ "buy":"33.15","high":"34.15","last":"33.15","low":"32.05","sell":"33.16","vol":"10532696.39199642"}}'
def test_should_stop_loss_shoud_return_true():
    result = macd._should_stop_loss(ticker, 34)
    if result == True:
        print('test_should_stop_loss_shoud_return_true pass')
    else:
        print('test_should_stop_loss_shoud_return_true failed')

def test_should_stop_loss_shoud_return_false():
    result = macd._should_stop_loss(ticker, 33)
    if result == False:
        print('test_should_stop_loss_shoud_return_false pass')
    else:
        print('test_should_stop_loss_shoud_return_false failed')

test_should_stop_loss_shoud_return_true()
test_should_stop_loss_shoud_return_false()

'''
test_is_slope_changing_to_positive_should_return_true()
test_is_slope_changing_to_positive_should_return_false()
test_long_signal_should_return_true()
test_long_signal_should_return_false()
test_short_signal_should_return_true()
test_short_signal_should_return_false()

test_is_dif_above_dea_back_n_periods_should_return_true()
test_is_dif_above_dea_back_n_periods_should_return_false()
test_is_dif_under_dea_back_n_periods_should_return_true()
test_is_dif_under_dea_back_n_periods_should_return_false()
'''

