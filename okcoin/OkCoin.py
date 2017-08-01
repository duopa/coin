# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果

import sys
import os
import threading
import time
import json
import traceback
import numpy
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
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print('======>>>process start at %(now)s ...' %{'now':now})
            with self._mutex:  # make sure only one thread is modifying counter at a given time
            #okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)
            #macd data
                kline = self._okcoinSpot.kline(self._symbol, self._type, 130, '')
                ticker = self._okcoinSpot.ticker(self._symbol)
                long_price = float(ticker['ticker']['buy'])
                avg_long_price = self._get_last_n_long_avg_price(2, 5)
                signal = self._macd_strategy.execute(kline, ticker, long_price, avg_long_price)

                if signal == 'sl':
                    print('\tstop loss')
                    #低于当前卖价卖出
                    price = float(ticker['ticker']['sell']) - 0.01
                    self._short(ticker, price)
                elif signal == 'l':
                    self._long(ticker, long_price)
                elif signal == 's':
                    #低于当前卖价卖出
                    price = float(ticker['ticker']['sell']) - 0.01
                    #上涨0.8%,两倍的交易成本
                    if self._is_reasonalbe_short_price(price, avg_long_price, 1.01):
                        self._short(ticker, price)
                        print('\t short price:%(price)s avgprice:%(avgprice)s' %{'price':price, 'avgprice':avg_long_price})
                print('---------------------------------------------------')
                print('')
        except:
            tb = traceback.format_exc()
            print(tb)

    # trade后更新本地funds缓存
    def _update_user_info(self):
        print('------OkCoin:update_user_info------')
        userinfo = json.loads(self._okcoinSpot.userinfo())
        print(userinfo)
        if userinfo['result']:
            self._funds = userinfo['info']['funds']
        else:
            print('_update_user_info failed<<<---')

    def _long(self, ticker, price):
        print('------OkCoin:long------')
        self._update_user_info()
        #为简单起见,如果有持仓,就不再买;缺点是失去了降低成本的可能性
        holding = float(self._funds['free'][self._symbol[0:3]])
        if holding > 0.01:
            return

        free_money = float(self._funds['free']['cny'])
        amount = self._amount_to_buy(price, free_money)
        self._print_trade('long', price, amount, ticker)
        if amount <= 0:
            return
        trade_result = json.loads(self._okcoinSpot.trade(self._symbol, 'buy', price, amount))
        if trade_result['result']:
            self._last_long_order_id = trade_result['order_id']
            print('\tlong order %(orderid)s placed successfully' %{'orderid': self._last_long_order_id})
            #从服务端order中获得更make sense
            #self._last_long_price = price
        else:
            print('\tlong order placed failed')
        #self._update_user_info()

    def _short(self, ticker, price):
        print('------OkCoin:short------')
        self._update_user_info()
        #available for sale
        afs = float(self._funds['free'][self._symbol[0:3]])
        self._print_trade('short', price, afs, ticker)
        if afs <= 0:
            return
        trade_result = json.loads(self._okcoinSpot.trade(self._symbol, 'sell', price, afs))
        if trade_result['result']:
            self._last_short_order_id = trade_result['order_id']
            print('\tshort order %(orderid)s placed successfully' %{'orderid': self._last_short_order_id})
        else:
            print('\tshort order placed failed')
            print('\t%(traderesult)s' %{'traderesult': trade_result})
        #self._update_user_info()

    def _amount_to_buy(self, price, free_money):        
        if self._symbol == 'ltc_cny':
            unit = 0.1
            rnd = 1
        elif self._symbol == 'btc_cny':
            unit = 0.01
            rnd = 2
        elif self._symbol == 'eth_cny':
            unit = 0.01
            rnd = 2

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
    def _is_reasonalbe_short_price(self, short_price, avg_long_price, multi):
        if short_price <= avg_long_price:
            return False

        if short_price < avg_long_price * multi:
            return False
        else:
            return True

    ### 获得前n次买入的平均价格
    def _get_last_n_long_avg_price(self, nlong, historycount):
        orderhistory = json.loads(self._okcoinSpot.orderHistory(self._symbol, '1', '1', historycount))
        if orderhistory['result']:
            orders = orderhistory['orders']
            totalprice = 0.0
            checknum = nlong
            long_price_his = []
            for i in range(-len(orders), 0):
                if len(long_price_his) < 2 and orders[i]['type'] == 'buy':
                    long_price_his.append(orders[i]['avg_price'])
                                
            return numpy.mean(long_price_his)
        else:
            return 0

    def _print_trade(self, direction, price, amount, ticker):
        date = datetime.fromtimestamp(int(ticker['date']))
        print('at %(datetime)s: %(direction)s price:%(price)s amount:%(amount)s' %{'datetime': date, 'direction':direction, 'price': price, 'amount':amount})
