# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果

import sys
import os
import threading
import time
import json
from .key import *
from .config import *
from strategy import *
from okcoin.OkcoinSpotAPI import OKCoinSpot
from datetime import datetime

class OkCoin:
    def __init__(self, symbol, type, frequency):
        self._apikey = api_key
        self._secretkey = secret_key
        self.stopped = False
        self._mutex = threading.Lock()   
        self._okcoinSpot = OKCoinSpot(url_cn,self._apikey,self._secretkey)
        self._macd_strategy = MacdStrategy()
        self._symbol = symbol
        self._type = type
        self._frequency = frequency
        self._funds = {}
        self._last_long_order_id = 0
        self._last_long_price = 0.0

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
        except Exception as e:
            print(e)

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
        except Exception as e:
            print(e)

    # trade后更新本地funds缓存
    def _update_user_info(self):
        userinfo = self._okcoinSpot.userinfo()
        self._funds = json.loads(userinfo)['info']['funds']

    def _long(self, ticker):
        #为简单起见,如果有持仓,就不再买;缺点是失去了降低成本的可能性
        holding = float(self._funds['free'][self._symbol])
        if holding > 0:
            return

        price = float(ticker['ticker']['buy'])
        amount = self._amount_to_buy(price)
        self._print_trade('long', price, amount, ticker)
        if amount <= 0:
            return
        trade_result = self._okcoinSpot.trade(self._symbol, 'buy', price, amount)
        if trade_result['result'] == True:
            self._last_long_order_id = trade_result['order_id']
            #从服务端order中获得更make sense
            self._last_long_price = price
        self._update_user_info()

    def _short(self, ticker):
        #低于当前卖价卖出
        price = float(ticker['ticker']['sell']) - 0.01
        #available for sale
        afs = float(self._funds['free'][self._symbol])        
        self._print_trade('short', price, afs, ticker)
        if afs <= 0:
            return
        #traderesult = self._okcoinSpot.trade(self._symbol, 'sell', price, afs)
        self._update_user_info()

    def _amount_to_buy(self, price):        
        if self._symbol == 'ltc_cny':
            unit = 0.1
            multi = 10
        elif self._symbol == 'btc_cny':
            unit = 0.01
            multi = 100
        elif self._symbol == 'eth_cny':
            unit = 0.01
            multi = 100
        
        free = float(self._funds['free']['cny'])
        amount = free / price
        if amount < unit:
            return 0
        
        #买入1/5
        amount = amount / 3
        if amount < unit:
            return unit
        else:
            return amount

    def _print_trade(self, direction, price, amount, ticker):
        date = datetime.fromtimestamp(int(ticker['date']))
        print('at %(datetime)s: %(direction)s price:%(price)s amount:%(amount)s' %{'price': price, 'amount':amount, 'direction':direction, 'datetime': date})

'''
#初始化apikey，secretkey,url
apikey = Key.api_key
secretkey = Key.secret_key
okcoinRESTURL = Config.url_cn

def get_kline():
    print(time.ctime())
    threading.Timer(1, get_kline).start()

#现货API
okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)

#macd data
kline = okcoinSpot.kline('btc_cny','5min', 100, '')

macd_strategy = Macd.MacdStrategy(kline)
macd_strategy.execute()

get_kline()

'''