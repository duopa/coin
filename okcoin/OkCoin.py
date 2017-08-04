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
from datetime import datetime, timedelta

class OkCoin:
    '''
    OkCoin
    '''
    def __init__(self, symbol, time_type, frequency):
        self._apikey = api_key
        self._secretkey = secret_key
        self.stopped = False
        self._mutex = threading.Lock()
        self._okcoinSpot = OKCoinSpot(url_cn, self._apikey, self._secretkey)
        self._macd_strategy = MacdStrategy()
        self._symbol = symbol
        self._coin_name = symbol[0:3]
        self._type = time_type
        self._frequency = frequency
        self._funds = {}
        self._ticker = {}
        self._last_long_order_id = 0
        self._last_short_order_id = 0
        self._last_trade_time = datetime.now() - timedelta(days = 1)

    #
    def run(self):
        '''
        https://stackoverflow.com/questions/44768688/python-how-to-do-a-periodic-non-blocking-lo
        '''
        try:
            self._update_user_info()
            while not self.stopped:                
                t = threading.Thread(target=self.process)
                t.setDaemon(True)  # so we don't need to track/join threads
                t.start()  # start the thread, this is non-blocking
                time.sleep(self._frequency)
        except:
            tb = traceback.format_exc()
            print(tb)

    #
    def process(self):
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print('======>>>process %(symbol)s start at %(now)s ...' %{'symbol': self._symbol, 'now':now})
            with self._mutex:  # make sure only one thread is modifying counter at a given time                
                if self._has_traded_in_near_periods_already():
                    return

                kline = self._okcoinSpot.kline(self._symbol, self._type, 130, '')
                self._ticker = self._okcoinSpot.ticker(self._symbol)
                last = float(self._ticker['ticker']['last'])
                long_price = float(self._ticker['ticker']['buy'])
                avg_long_price = self._get_last_n_long_avg_price(2, 6)
                holding = float(self._funds['free'][self._coin_name])
                signal = self._macd_strategy.execute(kline, last, long_price, avg_long_price, holding)

                if signal == 'sl':
                    print('\tstop loss')
                    #低于当前卖价卖出
                    price = float(self._ticker['ticker']['sell']) - 0.01
                    self._short(price)
                elif signal == 'l':
                    self._long(long_price)
                elif signal == 's':
                    #低于当前卖价卖出
                    price = float(self._ticker['ticker']['sell']) - 0.01
                    #上涨0.8%,两倍的交易成本
                    if self._is_reasonalbe_short_price(price, avg_long_price, 1.01):
                        self._short(price)
                        print('\tshort price:%(price)s avgprice:%(avgprice)s' %{'price':price, 'avgprice':avg_long_price})                
                print('---------------------------------------------------')
                print('')
        except:
            tb = traceback.format_exc()
            print(tb)

    def _update_user_info(self):
        '''
        : trade后更新本地funds缓存
        '''
        print('------OkCoin:update_user_info------')
        userinfo = json.loads(self._okcoinSpot.userinfo())
        print(userinfo)
        if userinfo['result']:
            self._funds = userinfo['info']['funds']
        else:
            print('_update_user_info failed<<<---')

    def _long(self, price):
        print('------OkCoin:long------')
        self._update_user_info()
        #为简单起见,如果有持仓,就不再买;缺点是失去了降低成本的可能性
        '''
        holding = float(self._funds['free'][self._symbol[0:3]])
        if holding > 0.01:
            return
        '''
        amount = self._amount_to_long(price)
        self._print_trade('long', price, amount)
        if amount <= 0:
            return
        trade_result = json.loads(self._okcoinSpot.trade(self._symbol, 'buy', price, amount))
        if trade_result['result']:
            self._last_long_order_id = trade_result['order_id']
            self._last_trade_time = datetime.now()
            print('\tlong order %(orderid)s placed successfully' %{'orderid': self._last_long_order_id})
        else:
            print('\t%(result)s' %{'result': trade_result})

    def _short(self, price):
        print('------OkCoin:short------')
        self._update_user_info()
        #available for sale
        afs = float(self._funds['free'][self._symbol[0:3]])
        self._print_trade('short', price, afs)
        if afs <= 0:
            return
        trade_result = json.loads(self._okcoinSpot.trade(self._symbol, 'sell', price, afs))
        if trade_result['result']:
            self._last_short_order_id = trade_result['order_id']
            self._last_trade_time = datetime.now()
            print('\tshort order %(orderid)s placed successfully' %{'orderid': self._last_short_order_id})
        else:
            print('\tshort order placed failed')
            print('\t%(result)s' %{'result': trade_result})

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
        amount = round(amount / 5, rnd)
        if amount < unit:
            return unit
        else:
            return amount

    def _amount_to_long(self, price):
        '''
        determine how many coins to buy base on total asset
        '''
        total = float(self._funds['asset']['total'])
        free_money = float(self._funds['free']['cny'])
        holding = float(self._funds['free'][self._coin_name])
        #如果某coin占总资金超过30%(可调整),停止买入此coin
        most_hold_percent = 0.3
        if holding * price >= total * most_hold_percent:
            print('\t%(coin_name)s poisition excess %(most_hold_percent)s money' %{'coin_name':self._coin_name, 'most_hold_percent': most_hold_percent})
            return 0

        if self._symbol == 'ltc_cny':
            unit = 0.1
            rnd = 1
        elif self._symbol == 'btc_cny':
            unit = 0.01
            rnd = 2
        elif self._symbol == 'eth_cny':
            unit = 0.01
            rnd = 2

        purchase = total / 5
        amount = 0
        if free_money >= purchase:
            amount = round(purchase / price, rnd)
        else:
            amount = round(free_money / price, rnd)

        if amount < unit:
            return unit
        else:
            return amount

    #有一个合理的涨幅才卖,只是能cover交易费用0.4%
    def _is_reasonalbe_short_price(self, short_price, avg_long_price, multi=1.01):
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
            long_price_his = []
            size = 0
            for i in range(-len(orders), 0):
                if size >= nlong:
                    break
                order = orders[i]
                if order['type'] == 'sell':
                    continue
                #status:-1:已撤销   0:未成交 1:部分成交 2:完全成交 4:撤单处理中
                if order['status'] in [-1, 0, 4]:
                    continue

                long_price_his.append(order['avg_price'])
                size = len(long_price_his)
            if size > 0:
                return numpy.mean(long_price_his)
            else:
                return 0
        else:
            return 0

    def _has_traded_in_near_periods_already(self, periods=3):
        '''
        : to avoid trading in n time pieces more than one time
        : ex: n=3 means never trade again in 3 time pieces
        '''
        if self._type == '1min':
            snds = 60
        elif self._type == '3min':
            snds = 180
        elif self._type == '5min':
            snds = 300
        else:
            snds = 180

        snds *= periods
        time_piece_start = datetime.now() - timedelta(seconds=snds)
        if self._last_trade_time >= time_piece_start:
            return True
        else:
            return False
    
    def _print_trade(self, direction, price, amount):
        date = datetime.fromtimestamp(int(self._ticker['date']))
        print('at %(datetime)s: %(direction)s price:%(price)s amount:%(amount)s' %{'datetime': date, 'direction':direction, 'price': price, 'amount':amount})
