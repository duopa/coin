import numpy
import talib
from .strategybase import StrategyBase 

class EmaCrossWithMacd(StrategyBase):
    """
    :http://www.forexfunction.com/trading-strategy-of-ema-crossover-with-macd
    """
    def __init__(self, **config):
        StrategyBase.__init__(self, **config)
        self._ema_quick_periods = self._config['ema_quick_periods']
        self._ema_slow_periods = self._config['ema_slow_periods']
        self._ema_quick = []
        self._ema_slow = []

    def execute(self, kline, **kwargs):
        close_list = self._get_close_from_kline(kline)
        close = numpy.array(close_list)
        self._ema_quick = talib.EMA(close, self._ema_quick_periods)
        self._ema_slow = talib.EMA(close, self._ema_slow_periods)
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
        if has_crossed:
            pass            

    def _is_ema_dead_cross(self):
        pass