# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果

import sys
import os
import threading
import time
import json
import math
import traceback
from datetime import datetime, timedelta
import numpy
from strategy import MacdStrategy
from okcoin.OkcoinSpotAPI import OKCoinSpot
from .key import api_key, secret_key
from .config import url_cn, config_3min, config_5min, log_path, signal_test_log_path
from common import Logger

class OkCoin:
    '''
    OkCoin
    '''
    def __init__(self, symbol, time_type, frequency):
        '''
        : symbol: btc_cny, ltc_cny, eth_cny
        : time_type: 1min, 3min, 5min...
        : frequency: seconds that execute strategy
        '''
        self._apikey = api_key
        self._secretkey = secret_key
        self._stopped = False
        self._symbol = symbol
        self._coin_name = symbol[0:3]
        self._type = time_type
        self._frequency = frequency
        self._funds = {}
        self._ticker = {}
        self._short_occurs = 0
        self._config = None
        self._last_trade_time = datetime.now() - timedelta(days=1)
        self._mutex = threading.Lock()
        self._strategy = None
        self._okcoin_spot = OKCoinSpot(url_cn, self._apikey, self._secretkey)
        self._logger = None #Logger('c:/logs', symbol)
        self._err_logger = None
    #------properties------
    @property
    def symbol(self):
        return self._symbol
    @symbol.setter
    def symbol(self, value):
        self._symbol = value

    @property
    def config(self):
        return self._config
    @config.setter
    def config(self, value):
        self._config = value
    
    @property
    def strategy(self):
        return self._strategy
    @strategy.setter
    def strategy(self, value):
        self._strategy = value
    #----------------------

    def run(self):
        '''
        https://stackoverflow.com/questions/44768688/python-how-to-do-a-periodic-non-blocking-lo
        '''
        try:
            self._logger = Logger(log_path, self.symbol)
            self._err_logger = Logger(log_path, self.symbol + '_err')
            print('---------------CONFIG---------------')
            for k, v in self.config.items():
                print("\t{0}: {1}".format(k, v))
            print('')
            self._logger.log('---------------start running---------------')
            self._update_user_info()
            while not self._stopped:
                thread = threading.Thread(target=self.process)
                thread.daemon = True  # so we don't need to track/join threads
                thread.start()  # start the thread, this is non-blocking
                time.sleep(self._frequency)
        except:
            tb = traceback.format_exc()
            self._err_logger.log(tb)

    def process(self):
        """
        :
        """
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print('======>>>process %(symbol)s %(type)s %(strategy)s start at %(now)s ...' 
            %{'symbol': self._symbol, 'type': self._type, 'strategy': self.strategy.name, 'now':now})
            #with self._mutex:  # make sure only one thread is modifying counter at a given time
            kline = self._okcoin_spot.kline(self._symbol, self._type, 130, '')
            self._ticker = self._okcoin_spot.ticker(self._symbol)
            ticker = self._ticker['ticker']
            last = float(ticker['last'])
            higt = float(ticker['high'])
            low = float(ticker['low'])
            long_price = float(ticker['buy'])
            short_price = float(ticker['sell'])
            avg_history_price = self._get_last_n_long_avg_price(2, 10)
            holding = float(self._funds['free'][self._coin_name])

            kwargs = {
                "last": last,
                "highest_price": higt,
                "lowest_price": low,
                "holding":holding,
                "long_price": long_price,
                "short_price": short_price,
                "avg_history_price": avg_history_price,
            }
            signal = self.strategy.execute(kline, **kwargs)

            # stop loss first priority
            if signal == 'sl':
                #低于当前卖价卖出
                short_price = short_price - 0.01
                self._stop_loss(short_price)

            if self._has_traded_in_near_periods_already(9):
                print('\tlast trade time {0}'.format(self._last_trade_time.strftime('%Y-%m-%d %H:%M%:S')))
                return

            if signal == 'l':
                self._long(long_price)
            elif signal == 's':
                short_price = short_price - 0.01
                self._short(short_price)
                self._logger.log('short price:%(price)s avgprice:%(avgprice)s' %{'price':short_price, 'avgprice':avg_history_price})
            print("------Parameters------")
            for k, v in kwargs.items():
                print("\t{0}: {1}".format(k, v))
            #print('{0}\n'.format(ticker))
        except:
            tb = traceback.format_exc()
            self._err_logger.log(tb)

    #-----------------------------------------------------------------------------------------------
    def run_signal_test(self):
        '''
        : only test signal, not trade
        '''
        try:
            self._logger = Logger(signal_test_log_path, self.symbol)
            print('---------------CONFIG---------------')
            for k, v in self.config.items():
                print("\t{0}: {1}".format(k, v))
            print('')
            self._logger.log('---------------start running---------------')
            self._update_user_info()
            while not self._stopped:
                thread = threading.Thread(target=self.process_signal_test)
                thread.daemon = True  # so we don't need to track/join threads
                thread.start()  # start the thread, this is non-blocking
                time.sleep(self._frequency)
        except:
            tb = traceback.format_exc()
            self._logger.log(tb)

    def process_signal_test(self):
        """
        :
        """
        try:
            print("------DEBUG------")
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print('======>>>process %(symbol)s %(type)s start at %(now)s ...' %{'symbol': self._symbol, 'type': self._type, 'now':now})
            with self._mutex:  # make sure only one thread is modifying counter at a given time
                kline = self._okcoin_spot.kline(self._symbol, self._type, 130, '')
                self._ticker = self._okcoin_spot.ticker(self._symbol)
                ticker = self._ticker['ticker']
                last = float(ticker['last'])
                long_price = float(ticker['buy'])
                short_price = float(ticker['sell'])
                avg_long_price = self._get_last_n_long_avg_price(2, 10)
                holding = float(self._funds['free'][self._coin_name])

                kwargs = {'last': last, 'long_price': long_price, 'short_price': short_price, 'avg_long_price': avg_long_price, 'holding':holding}
                signal = self.strategy.execute(kline, **kwargs)

                if signal != "":
                    self._logger.log(signal)
        except:
            tb = traceback.format_exc()
            self._logger.log(tb)
    #-----------------------------------------------------------------------------------------------

    def _update_user_info(self):
        '''
        : trade后更新本地funds缓存
        '''
        print('------OkCoin: update_user_info------')
        userinfo = json.loads(self._okcoin_spot.userinfo())
        print(userinfo)
        if userinfo['result']:
            self._funds = userinfo['info']['funds']
        else:
            self._logger.log('ERROR:_update_user_info failed')

    def _long(self, price):
        print('------OkCoin: long------')
        self._update_user_info()
        amount = self._amount_to_long(price)
        self._print_trade('long', price, amount)
        if amount <= 0:
            return
        trade_result = json.loads(self._okcoin_spot.trade(self._symbol, 'buy', price, amount))
        if trade_result['result']:
            #:reset short_occurs, it's better to check this long trade really filled
            self._short_occurs = 0
            order_id = trade_result['order_id']
            self._last_trade_time = datetime.now()
            self._logger.log('long order %(orderid)s placed successfully' %{'orderid': order_id})
            self._check_order_status(order_id)
        else:
            msg = '{0}'.format(trade_result)
            print('\t' + msg)
            self._logger.log(msg)

    def _stop_loss(self, price):
        print('------OkCoin: stop loss------')
        self._logger.log('OkCoin: STOP LOSS')
        self._update_user_info()
        amount = self._amount_to_short(True)
        self._do_short(price, amount)

    def _short(self, price):
        print('------OkCoin: short------')
        self._update_user_info()
        amount = self._amount_to_short()
        self._do_short(price, amount)

    def _do_short(self, price, amount):
        if amount <= 0:
            self._logger.log('no engough coin for sale')
            return
        self._print_trade('short', price, amount)
        trade_result = json.loads(self._okcoin_spot.trade(self._symbol, 'sell', price, amount))
        if trade_result['result']:
            #:increase short_occurs
            short_occurs_len = len(self.config['short_ratio'])
            self._short_occurs = self._short_occurs + 1 if self._short_occurs < (short_occurs_len -1) else self._short_occurs
            order_id = trade_result['order_id']
            self._last_trade_time = datetime.now()
            self._logger.log('short order %(orderid)s placed successfully' %{'orderid': order_id})
            self._check_order_status(order_id)
        else:
            msg = '{0}'.format(trade_result)
            print('\t' + msg)
            self._logger.log(msg)

    def _check_order_status(self, order_id):
        timer = threading.Timer(15, self._do_check_order_status, [order_id])
        timer.daemon = True
        timer.start()

    def _do_check_order_status(self, order_id):
        order_result = json.loads(self._okcoin_spot.order_info(self.symbol, order_id))
        if not order_result['result']:
            return
        else:
            orders = order_result['orders']
            if not orders or orders[0]['status'] != 0: #0: not filled
                return

        result = json.loads(self._okcoin_spot.cancel_order(self.symbol, order_id))
        if result['result']:
            self._last_trade_time = datetime.now() - timedelta(days=1)
            msg = 'order {0} cancelled successfully'.format(order_id)
            self._logger.log(msg)
        else:
            msg = 'order {0} cancelled FAILED \n{1}'.format(order_id, result)
            self._logger.log(msg)

    def _amount_to_short(self, stop_loss=False):
        lowest_unit, rnd = self._trade_config()
        #available for sale
        afs = float(self._funds['free'][self._coin_name])
        if afs < lowest_unit:
            return 0

        amount = 0
        #if stop loss, just short all coins
        if stop_loss:
            amount = afs
        else:
            #short part of all, doing this is in case of price keep going up after a short break; is this a good strategy or not need to be test
            amount = afs * self.config['short_ratio'][self._short_occurs]
            if amount < lowest_unit:
                #amount = afs
                amount = lowest_unit

        return math.trunc(amount * 1000)/1000

    def _amount_to_long(self, price):
        '''
        determine how many coins to buy base on total asset
        '''
        total = float(self._funds['asset']['total'])
        free_money = float(self._funds['free']['cny'])
        holding = float(self._funds['free'][self._coin_name])
        #如果某coin占总资金超过20%(可调整),停止买入此coin
        most_hold_percent = self.config['coin_most_hold_ratio']
        if holding * price >= total * most_hold_percent:
            msg = '{coin_name} poisition excess {most_hold_percent}% money'.format(**{'coin_name':self._coin_name, 'most_hold_percent': most_hold_percent * 100})
            self._logger.log(msg)
            return 0

        lowest_unit, rnd = self._trade_config()
        purchase = total * self.config['long_total_ratio']
        amount = 0
        if free_money >= purchase:
            amount = purchase / price #round(purchase / price, rnd)
        else:
            amount = free_money / price #round(free_money / price, rnd)

        if amount < lowest_unit:
            amount = 0

        return math.trunc(amount * 1000)/1000
    #------------------------------------------------------------------------------------------------
    def _get_last_n_long_avg_price(self, nlong, historycount):
        '''
        : 获得前n次买入的平均价格
        : 20170805: add weight, the last buy weight 0.8, the rest share 0.2
        '''
        orderhistory = json.loads(self._okcoin_spot.order_history(self._symbol, '1', '1', historycount))
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
                # weighted
                weighted_avg = 0
                # the latest long price weight
                latest_weigth = 0.8 if size > 1 else 1
                other_weight = 0.2 / (size -1) if size > 1 else 0
                for i in range(0, size):
                    if i == 0:
                        weighted_avg += latest_weigth * long_price_his[i]
                    else:
                        weighted_avg += other_weight * long_price_his[i]
                return round(weighted_avg, 4)
                #return numpy.mean(long_price_his)
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
        msg = 'at {datetime}: {direction} price: {price} amount: {amount}'.format(**{'datetime': date, 'direction':direction, 'price': price, 'amount':amount})
        self._logger.log(msg)
        print('\t' + msg)

    def _trade_config(self):
        lowest_unit = 0.01
        rnd = 1
        if self._symbol == 'ltc_cny':
            lowest_unit = 0.1
            rnd = 1
        elif self._symbol == 'btc_cny':
            lowest_unit = 0.01
            rnd = 2
        elif self._symbol == 'eth_cny':
            lowest_unit = 0.01
            rnd = 2
        return lowest_unit, rnd
