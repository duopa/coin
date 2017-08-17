
from datetime import datetime
import numpy
import talib

class StrategyBase:
    """
    """
    def __init__(self, **config):
        self._config = config
        self._stop_loss_count_down = 0
        self._kline = []

    def execute(self, kline, **kwargs):
        '''
        : execute strategy
        '''        
        last = kwargs['last']
        long_price = kwargs['long_price']
        short_price = kwargs['short_price']
        avg_long_price = kwargs['avg_long_price']
        holding = kwargs['holding']

        if self._should_stop_loss(last, avg_long_price, holding):
            return 'sl'
        elif self._long_signal(long_price):
            return 'l'
        elif self._short_signal(short_price, avg_long_price):
            return 's'
        else:
            return ''

    def _should_stop_loss(self, last, avg_long_price, holding):
        '''
        : stop loss signal
        '''
        stop_loss_ratio = self._config['stop_loss_ratio']
        if holding < 0.01:
            return False
        if last <= (avg_long_price * (1- stop_loss_ratio)):
            self._stop_loss_count_down = self._config['stop_loss_count_down']
            return True
        return False

    def _long_signal(self, long_price):
        pass

    def _short_signal(self, short_price, avg_history_price):
        pass

    def _is_reasonalbe_short_price(self, short_price, avg_history_price):
        '''
        : Only when short_price higher than avg price certain percent, then short
        '''
        if short_price <= avg_history_price:
            return False
        stop_profit_ratio = self._config['stop_profit_ratio']
        if short_price < avg_history_price * (1 + stop_profit_ratio):
            return False
        else:
            return True

    #--------------------------------HELPER-------------------------------------------------------
    def _get_macd(self):
        close_list = self._get_close_from_kline()
        close = numpy.array(close_list)
        #dif, dea, diff - dea?
        return talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    def _get_ema(self, periods):
        close_list = self._get_close_from_kline()
        close = numpy.array(close_list)
        return talib.EMA(close, periods)

    def _get_close_from_kline(self):
        close = []
        for arr in self._kline:
            close.append(arr[4])
        return close

    def _get_open_from_kline(self):
        opens = []
        for arr in self._kline:
            opens.append(arr[1])
        return opens
