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
        '''
        : macd_long_signal as first long point, macd slope change always before ema corss, this is try to long at low price
        '''
        macd_long_signal = self._is_slope_changing_to_positive() and self._is_long_price_under_highest_price_percent(long_price)
        is_golden_cross = self._is_ema_golden_cross()
        if macd_long_signal or is_golden_cross:
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
        and self._ema_quick[-2] >= self._ema_slow[-2] \
        and self._ema_quick[-3] < self._ema_slow[-3]
        check_periods = self._ema_slow_periods
        i = -3
        if has_crossed:
            while i >= -check_periods:
                if self._ema_quick[i] < self._ema_slow[i]:
                    i -= 1
                    continue
                elif self._ema_quick[i-1] > self._ema_slow[i-1] \
                    and self._ema_quick[i-2] > self._ema_slow[i-2] \
                    and self._ema_quick[i-3] > self._ema_slow[i-3]:
                    return False
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
        slow_max = numpy.max(slow_arr)
        slow_min = numpy.min(slow_arr)
        if (slow_max - slow_min) / slow_avg < 0.01:
            return True
        else:
            return False
        '''
        quick_avg = numpy.average(quick_arr)
        if abs(slow_avg - quick_avg) / slow_avg < 0.001:
            return True
        else:
            return False
        '''

    def _is_slope_changing_to_positive(self):
        '''
        : whether slope of dif line head up
        '''
        if len(self._macd) < 12:
            return False
        temp = self._macd[-12:]
        index = numpy.argmin(temp)
        if len(temp) - index == 3 and self._macd[-1] > self._macd[-2]:#最低点在倒数第三个表面方向向上(可能要调整)
            return True
        else:
            return False

    def _is_long_price_under_highest_price_percent(self, long_price):
        '''
        : use EMA slow as highest price instead, this is out of EMA avg price make more sense than absolute highest price
        '''
        highest_price, index_negtive = self._get_last_ema_dead_cross_avg_price(5, 30)
        # make sure the distance is enough, or it will long too early
        if abs(index_negtive) < (self._ema_quick_periods + self._ema_slow_periods): # default 30 = 9 + 21
            return False
        else:
            #当long_price >= highest_price时,认为是在创新高,买入
            if long_price >= highest_price:
                return True
            else:
                percent = self._config["long_price_down_ratio"]
                diff = highest_price * (1 - percent)
                if long_price <= diff:
                    return True
                else:
                    return False
