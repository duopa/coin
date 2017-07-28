# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果

import sys
import os
import threading
import time
import json
import traceback
from .key import *
from .config import *
from strategy import *
from okcoin.OkcoinSpotAPI import OKCoinSpot
from datetime import datetime

class OkCoin:
    '''
    OkCoin
    '''
    def __init__(self, symbol, type, frequency):
        self._apikey = api_key
        self._secretkey = secret_key
        self.stopped = False
        self._mutex = threading.Lock()
        self._okcoinSpot = OKCoinSpot(url_cn, self._apikey, self._secretkey)
        self._macd_strategy = MacdStrategy()
        self._symbol = symbol
        self._type = type
        self._frequency = frequency
        self._funds = {}
        self._last_long_order_id = 0
        self._last_long_price = 0.0
        self._last_short_order_id = 0

    #
    def run(self):
        '''
        https://stackoverflow.com/questions/44768688/python-how-to-do-a-periodic-non-blocking-lo
        '''
        try:
            self._update_user_info()
            while not self.stopped:
                time.sleep(self._frequency)
                t = threading.Thread(target=self.process)
                t.setDaemon(True)  # so we don't need to track/join threads
                t.start()  # start the thread, this is non-blocking
        except:
            tb = traceback.format_exc()
            print(tb)

    #
    def process(self):
        try:
            with self._mutex:  # make sure only one thread is modifying counter at a given time
            #okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)
            #macd data
                kline = self._okcoinSpot.kline(self._symbol, self._type, 130, '')
                ticker = self._okcoinSpot.ticker(self._symbol)
                #这里的self._last_long_price 从服务端的order 获得更make sense
                if self._macd_strategy.should_stop_loss(ticker, self._last_long_price):
                    signal = 's'
                else:
                    signal = self._macd_strategy.execute(kline)

                if signal == 'l':
                    self._long(ticker)
                elif signal == 's':
                    self._short(ticker)
                print('---------------------------------------------')
                print('')
        except:
            tb = traceback.format_exc()
            print(tb)

    # trade后更新本地funds缓存
    def _update_user_info(self):
        print('------OkCoin:update_user_info------')
        userinfo = json.loads(self._okcoinSpot.userinfo())
        if userinfo['result']:
            self._funds = userinfo['info']['funds']
        else:
            print('_update_user_info failed<<<---')

    def _long(self, ticker):
        print('------OkCoin:long------')
        #为简单起见,如果有持仓,就不再买;缺点是失去了降低成本的可能性
        holding = float(self._funds['free'][self._symbol[0:3]])
        if holding > 0:
            return

        price = float(ticker['ticker']['buy'])
        free_money = float(self._funds['free']['cny'])
        amount = self._amount_to_buy(price, free_money)
        self._print_trade('long', price, amount, ticker)
        if amount <= 0:
            return
        trade_result = self._okcoinSpot.trade(self._symbol, 'buy', price, amount)
        if trade_result['result']:
            self._last_long_order_id = trade_result['order_id']
            print('  long order %(orderid)s placed successfully' %{'orderid': self._last_long_order_id})
            #从服务端order中获得更make sense
            self._last_long_price = price
        else:
            print('  long order placed failed')
        self._update_user_info()

    def _short(self, ticker):
        print('------OkCoin:short------')
        #低于当前卖价卖出
        price = float(ticker['ticker']['sell']) - 0.01       
        if not self._is_reasonalbe_short_price(price, 1.008):#上涨0.8,两倍的交易成本
            return 
        #available for sale
        afs = float(self._funds['free'][self._symbol[0:3]])        
        self._print_trade('short', price, afs, ticker)
        if afs <= 0:
            return
        trade_result = self._okcoinSpot.trade(self._symbol, 'sell', price, afs)
        if trade_result['result']:
            self._last_short_order_id = trade_result['order_id']
            print('  short order %(orderid)s placed successfully' %{'orderid': self._last_short_order_id})
            #从服务端order中获得更make sense
            self._last_long_price = price
        else:
            print('  short order placed failed')
        self._update_user_info()

    def _amount_to_buy(self, price, free_money):        
        if self._symbol == 'ltc_cny':
            unit = 0.1
            rnd = 1
            multi = 10
        elif self._symbol == 'btc_cny':
            unit = 0.01
            rnd = 2
            multi = 100
        elif self._symbol == 'eth_cny':
            unit = 0.01
            rnd = 2
            multi = 100
        
        amount = free_money / price
        if amount < unit:
            return 0
        
        #买入1/5
        amount = round(amount / 3, rnd)
        if amount < unit:
            return unit
        else:
            return amount

    #有一个合理的涨幅才卖,只是能cover交易费用0.4%
    def _is_reasonalbe_short_price(self, price, multi):
        if price < self._last_long_price * multi:
            return False
        else:
            return True


    def _print_trade(self, direction, price, amount, ticker):
        date = datetime.fromtimestamp(int(ticker['date']))
        print('at %(datetime)s: %(direction)s price:%(price)s amount:%(amount)s' %{'datetime': date, 'direction':direction, 'price': price, 'amount':amount})
