# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果


import sys
import os
import threading
import time
import json
import Key
import Config
lib_path = os.path.abspath(os.path.join('strategy'))
sys.path.append(lib_path)
import Macd
from OkcoinSpotAPI import OKCoinSpot
from datetime import datetime

class OkCoin:
    def __init__(self, symbol, type, frequency):
        self._apikey = Key.api_key
        self._secretkey = Key.secret_key
        self.stopped = False
        self._mutex = threading.Lock()   
        self._okcoinSpot = OKCoinSpot(Config.url_cn,self._apikey,self._secretkey)
        self._macd_strategy = Macd.MacdStrategy()
        self._symbol = symbol
        self._type = type
        self._frequency = frequency
        self._funds = {}

    #
    def process(self):
        with self._mutex:  # make sure only one thread is modifying counter at a given time
            #okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)
            #macd data
            kline = self._okcoinSpot.kline(self._symbol, self._type, 130, '')
            ticker = self._okcoinSpot.ticker(self._symbol)
            #macd_strategy = Macd.MacdStrategy(kline)
            signal = self._macd_strategy.execute(kline)
            if signal == 'l':
                ticker = self._okcoinSpot.ticker(self._symbol)
                date = datetime.fromtimestamp(int(ticker['date']))
                print('at %(datetime)s: long %(price)s' %{'price': ticker['ticker']['buy'],'datetime': date})
            elif signal == 's':
                ticker = self._okcoinSpot.ticker(self._symbol)
                date = datetime.fromtimestamp(int(ticker['date']))
                print('at %(datetime)s: short %(price)s' %{'price': ticker['ticker']['sell'], 'datetime': date})
           
    
    #
    def run(self): 
        '''
        https://stackoverflow.com/questions/44768688/python-how-to-do-a-periodic-non-blocking-lo
        '''  
        self._update_user_info()
        while not self.stopped:  
            time.sleep(self._frequency)          
            t = threading.Thread(target=self.process)
            t.setDaemon(True)  # so we don't need to track/join threads
            t.start()  # start the thread, this is non-blocking

    # trade后更新本地funds缓存
    def _update_user_info(self):
        userinfo = self._okcoinSpot.userinfo()
        self._funds = json.load(userinfo)['info']['funds']

    def _long(self, ticker):
        price = float(ticker['ticker']['buy']) + 0.01
        self._okcoinSpot.trade(self._symbol, 'buy', price, )
        self._update_user_info()

    def _short(self, ticker):
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
        #买入1/5
        amount = free / price
        if amount < unit:
            return 0
        
        #买入1/5
        amount = amount / 5
        if amount < unit:
            return unit
        else:
            return amount

#        
okcoin = OkCoin('ltc_cny', '1min', 55)
okcoin.run()

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