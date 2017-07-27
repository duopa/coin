import sys
import os
import json
from strategy import *

macd = MacdStrategy()

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