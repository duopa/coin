
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
        self._params = {}
        self._ema_quick = []
        self._ema_slow = []
        self._macd = []
        self._macdsignal = []
        self._macdhist = []
        self._close = []
        self._stop_profit_ratio = 0.01
    
    @property
    def name(self):
        return ''

    @property
    def symbol(self):
        return self._symbol
    @symbol.setter
    def symbol(self, value):
        self._symbol = value
        self._stop_profit_ratio = self._config["stop_profit_" + value[0:3]]

    @property
    def macd(self):
        return self._macd

    @property
    def macdsignal(self):
        return self._macdsignal

    @property
    def macdhist(self):
        return self._macdhist

    @property
    def ema_quick(self):
        return self._ema_quick

    @property
    def ema_slow(self):
        return self._ema_slow

    @property
    def close(self):
        return self._close

    def execute(self, kline, **kwargs):
        '''
        : execute strategy
        '''
        self._params = kwargs
        last = kwargs['last']
        long_price = kwargs['long_price']
        short_price = kwargs['short_price']
        avg_history_price = kwargs['avg_history_price']
        holding = kwargs['holding']

        if self._should_stop_loss(last, avg_history_price, holding):
            return 'sl'
        elif self._long_signal(long_price):
            return 'l'
        elif self._short_signal(short_price, avg_history_price):
            return 's'
        else:
            return ''

    def _should_stop_loss(self, last, avg_history_price, holding):
        '''
        : stop loss signal
        '''
        stop_loss_ratio = self._config['stop_loss_ratio']
        if holding < 0.01:
            return False
        if last <= (avg_history_price * (1- stop_loss_ratio)):
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

        if short_price < avg_history_price * (1 + self._stop_profit_ratio):
            return False
        else:
            return True

    #--------------------------------HELPER-------------------------------------------------------
    def _get_macd(self):
        close = numpy.array(self.close)
        #dif, dea, diff - dea?
        return talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    def _get_ema(self, periods):
        close = numpy.array(self.close)
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

    def _get_last_ema_dead_cross_avg_price(self, quick_periods, slow_periods):
        '''
        : return the slow ema value and index when EMA dead cross
        '''
        close = numpy.array(self.close)
        ema_quick = talib.EMA(close, quick_periods)
        ema_slow = talib.EMA(close, slow_periods)
        index = -1
        for i in range(-1, -len(ema_slow), -1):
            if ema_quick[i] < ema_slow[i]:
                continue
            else:
                index = i
                break

        return ema_slow[index], index