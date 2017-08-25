from .strategybase import StrategyBase
import numpy
import talib
import math

class EmaCrossWithMacdStrategy(StrategyBase):
    """
    :http://www.forexfunction.com/trading-strategy-of-ema-crossover-with-macd
    """
    def __init__(self, **config):
        StrategyBase.__init__(self, **config)
        self._ema_quick_periods = self._config['ema_quick_periods']
        self._ema_slow_periods = self._config['ema_slow_periods']        

    @property
    def name(self):
        return "EmaCrossWithMacd"

    def execute(self, kline, **kwargs):
        self._kline = kline
        self._close = self._get_close_from_kline()
        #dif, dea, diff - dea?
        self._macd, self._macdsignal, self._macdhist = self._get_macd()        
        self._ema_quick = self._get_ema(self._ema_quick_periods)
        self._ema_slow = self._get_ema(self._ema_slow_periods)
        return super().execute(kline, **kwargs)

    def _should_stop_loss(self, last, avg_history_price, holding):
        return super()._should_stop_loss(last, avg_history_price, holding)

    def _long_signal(self, long_price):
        '''
        : macd_long_signal as first long point, macd slope change always before ema corss, this is try to long at low price
        '''
        '''
        macd_golden_cross = self._is_macd_golden_cross()
        macd_slope_signal = self._is_slope_changing_to_positive()
        macd_signal = (macd_golden_cross or macd_slope_signal) and self._is_long_price_under_last_dead_cross_price_percent(long_price)
        '''
        macd_signal = self._is_macd_golden_cross() #and self._is_long_price_under_last_dead_cross_price_percent(long_price)
        ema_golden_cross = self._is_ema_golden_cross() and self._is_long_price_under_highest_price_percent(long_price)
        if macd_signal or ema_golden_cross:
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
        has_crossed = self.ema_quick[-1] > self.ema_slow[-1] \
        and self.ema_quick[-2] > self.ema_slow[-2] \
        and self.ema_quick[-3] > self.ema_slow[-3] \
        and self.ema_quick[-4] >= self.ema_slow[-4] \
        and self.ema_quick[-5] < self.ema_slow[-5] \
        and self.ema_quick[-1] > self.ema_quick[-2] \
        and self.ema_quick[-2] > self.ema_quick[-3] \
        and self.ema_quick[-3] > self.ema_quick[-4]
        
        check_periods = self._ema_slow_periods
        i = -3
        if has_crossed:
            #:make sure slope of after cross bigger than before
            #:this need improve
            """
            if self._ema_quick[-1] - self.ema_quick[-3] < self.ema_quick[-3] - self.ema_quick[-5]:
                return False
            """
            #:make sure price not go up too much when long
            price_uped = self.close[-1] - self.close[-5]
            if (price_uped / self.close[-5]) > 0.01:
                return False
            #make sure quick under slow _ema_slow_periods perirods
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
        """
        """
        is_on_ranging = self._is_on_ranging()
        #: if quick from top approching slow enough, then deem it's dead cross
        approch_a = (self._ema_quick[-1] - self._ema_slow[-1]) / self._ema_slow[-1]
        approch_b = (self._ema_quick[-2] - self._ema_slow[-2]) / self._ema_slow[-2]
        if math.floor(self._ema_quick[-2]) > math.floor(self._ema_quick[-1]) \
        and 0 < approch_a < 0.0005 and 0 < approch_b < 0.0005 \
        and not is_on_ranging:
            return True

        has_crossed = self._ema_quick[-1] < self._ema_slow[-1] \
        and self._ema_quick[-2] >= self._ema_slow[-2] \
        and self._ema_quick[-3] > self._ema_slow[-3]
        if has_crossed and self._macdhist[-1] < 0:
            return True
        else:
            return False
    #-----------------------------------------------------------------------------------------------
    def _is_macd_golden_cross(self):
        """
        : 1: quick cross slow from bottom to above
        : 2: the dea must below the closest negative hist
        : 3: the quick must below the slow at least 9 periods
        """
        has_crossed = self._macd[-1] < 0 and self._macdsignal[-1] < 0 \
        and self._macd[-1] > self._macd[-2] \
        and self._macd[-1] > self._macdsignal[-1] \
        and self._macd[-2] >= self._macdsignal[-2] \
        and self._macd[-3] < self._macdsignal[-3]
        if has_crossed:
            min_hist = numpy.min(self._macdhist[-90:])
            #make sure the last dea smaller than the min hist bar
            if min_hist >= 0 or or math.isnan(min_hist) or self._macdsignal[-1] > (min_hist * 2):# okcoin's macd hist doubled? don't why?
                return False
            else:
                #check if diff was under dea for last at least 21 periods
                i = -3
                while i >= -12:
                    if self._macd[i] < self._macdsignal[i]:
                        i -= 1
                        continue
                    else:
                        return False
                return True
        return False
    #-----------------------------------------------------------------------------------------------
    def _is_on_ranging(self):
        #arr_len = self._ema_quick_periods + self._ema_slow_periods
        arr_len = self._ema_slow_periods
        slow_arr = self._ema_slow[-arr_len:]
        quick_arr = self._ema_quick[-arr_len:]
        slow_avg = numpy.average(slow_arr)
        slow_max = numpy.max(slow_arr)
        slow_min = numpy.min(slow_arr)
        if (slow_max - slow_min) / slow_avg <= 0.002:
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

    def _is_long_price_under_last_dead_cross_price_percent(self, long_price):
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

    def _is_long_price_under_highest_price_percent(self, long_price):
        highest_price = self._params['highest_price']
        percent = self._config["long_price_down_ratio"]
        diff = highest_price * (1 - percent)
        if long_price <= diff:
            return True
        else:
            return False
