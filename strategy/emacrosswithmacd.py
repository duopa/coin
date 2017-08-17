from .strategybase import StrategyBase
import numpy
import talib

class EmaCrossWithMacdStrategy(StrategyBase):
    """
    :http://www.forexfunction.com/trading-strategy-of-ema-crossover-with-macd
    """
    def __init__(self, **config):
        StrategyBase.__init__(self, **config)
        self._ema_quick_periods = self._config['ema_quick_periods']
        self._ema_slow_periods = self._config['ema_slow_periods']
        self._ema_quick = []
        self._ema_slow = []
        self._macd = []
        self._macdsignal = []
        self._macdhist = []

    def execute(self, kline, **kwargs):
        self._kline = kline
        #dif, dea, diff - dea?
        self._macd, self._macdsignal, self._macdhist = self._get_macd()        
        self._ema_quick = self._get_ema(self._ema_quick_periods)
        self._ema_slow = self._get_ema(self._ema_slow_periods)
        return super().execute(kline, **kwargs)

    def _should_stop_loss(self, last, avg_long_price, holding):
        return super()._should_stop_loss(last, avg_long_price, holding)

    def _long_signal(self, long_price):
        is_golden_cross = self._is_ema_golden_cross()
        if is_golden_cross:
            return True
        else:
            return False

    def _short_signal(self, short_price, avg_history_price):
        if not self._is_reasonalbe_short_price(short_price, avg_history_price):
            return False
        is_dead_cross = self._is_ema_dead_cross()
        if is_dead_cross:
            return True
        else:
            return False
    #--------------------------------Conditions---------------------------------------------------
    def _is_ema_golden_cross(self):
        has_crossed = self._ema_quick[-1] > self._ema_slow[-1] \
        and self._ema_quick[-2] <= self._ema_slow[-2] \
        and self._ema_quick[-3] < self._ema_slow[-3]
        is_on_ranging = self._is_on_ranging()
        if has_crossed and not is_on_ranging and self._macdhist[-1] > 0:
            return True
        else:
            return False

    def _is_ema_dead_cross(self):
        has_crossed = self._ema_quick[-1] < self._ema_slow[-1] \
        and self._ema_quick[-2] >= self._ema_slow[-2] \
        and self._ema_quick[-3] > self._ema_slow[-3]
        is_on_ranging = self._is_on_ranging()
        if has_crossed and not is_on_ranging and self._macdhist[-1] < 0:
            return True
        else:
            return False

    def _is_on_ranging(self):
        arr_len = self._ema_quick_periods + self._ema_slow_periods
        slow_arr = self._ema_slow[-arr_len:]
        quick_arr = self._ema_quick[-arr_len:]
        slow_avg = numpy.average(slow_arr)
        quick_avg = numpy.average(quick_arr)
        if abs(slow_avg - quick_avg) / slow_avg < 0.001:
            return True
        else:
            return False