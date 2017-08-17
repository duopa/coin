"""
"""
from .strategybase import StrategyBase
from datetime import datetime
import numpy
import talib

class MacdStrategy(StrategyBase):
    '''
    :
    '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pre_highest_price = 0
        self._give_up_long_count_down = 1
        self._macd = []
        self._macdsignal = []
        self._macdhist = []
    #-----------------------------------------------------------------------------------------------
    #def execute(self, kline, last, long_price, avg_long_price, holding):
    def  execute(self, kline, **kwargs):
        '''
        : execute strategy
        '''
        #now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #print('at:%(datetime)s MacdStrategy executing' %{'datetime': now})

        self._kline = kline
        #dif, dea, diff - dea?
        self._macd, self._macdsignal, self._macdhist = self._get_macd()
        return super().execute(kline, **kwargs)
    #-----------------------------------------------------------------------------------------------
    def _long_signal(self, long_price):
        '''
        : long signal
        '''
        result = (self._macd[-1] < 0) and (self._macdsignal[-1] < 0) \
        and self._is_slope_changing_to_positive() \
        and self._is_hist_under_zero_back_n_periods(8) \
        and not self._is_hist_close_to_zero_for_n_periods() \
        and (self._is_long_price_under_highest_price_percent2(long_price) or self._is_dea_under_zero_back_n_periods(long_price)) \
        and (self._is_dif_under_dea_back_n_periods() or self._is_lowest_hist() or self._is_pre_dif_dea_far_enough())

        #volumn_signal = self._is_volumn_up_sharply(kline, 20, 30)
        if result:
            #is_in_give_up_counting = self._is_in_give_up_long_counting(kline)
            is_in_stop_loss_counting = self._is_in_stop_loss_counting()
            if is_in_stop_loss_counting:
                return False
            else:
                return True
        else:
            return False
    #-----------------------------------------------------------------------------------------------
    def _short_signal(self, short_price, avg_history_price):
        '''
        : short signal
        '''
        if not self._is_reasonalbe_short_price(short_price, avg_history_price):
            return False
        isslopechangingtonegtive = self._is_slope_changing_to_negtive()
        isdifabovedeabacknperiods = self._is_dif_above_dea_back_n_periods(8)
        ishighesthist = self._is_highest_hist()
        ispredifdeafarenough = self._is_pre_dif_dea_far_enough()
        dif_above_zero_back_n_periods = self._is_dif_above_zero_back_n_periods(6)
        '''
        try:
            print('\tshot_signal: %(a)s %(b)s %(c)s %(d)s' %{'a': isslopechangingtonegtive, 'b': isdifabovedeabacknperiods, 'c': ishighesthist, 'd':ispredifdeafarenough})
        except:
            pass
        '''
        return isslopechangingtonegtive \
        and dif_above_zero_back_n_periods \
        and (isdifabovedeabacknperiods or ishighesthist or ispredifdeafarenough)
    #-----------------------------------------------------------------------------------------------
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
    #-----------------------------------------------------------------------------------------------
    def _is_slope_changing_to_positive(self):
        '''
        : whether slope of dif line head up
        : 找一个更好的算法确定方向改变
        '''
        #最低点法判定方向改变向上
        if len(self._macd) < 12:
            return False
        temp = self._macd[-12:]
        #min = numpy.min(temp)
        #index = temp.index(min)
        index = numpy.argmin(temp)
        #会导致交易两次
        #if(2 <= len(temp) - index <= 3):
        if len(temp) - index == 3 and self._macd[-1] > self._macd[-2]:#最低点在倒数第三个表面方向向上(可能要调整)
            return True
        else:
            return False
    #-----------------------------------------------------------------------------------------------
    def _is_slope_changing_to_negtive(self):
        '''
        : whether slope of diff line heading down
        '''
        #最高点法判定方向改变向下
        if len(self._macd) < 12:
            return False
        temp = self._macd[-12:]
        #max = numpy.min(temp)
        #index = temp.index(max)
        index = numpy.argmax(temp)
        #会导致交易两次
        if 2 <= len(temp) - index <= 3:
        #可能会错过
        #if(len(temp) - index == 2):
            return True
        else:
            return False
        '''
        if (linedata[-1] <= linedata[-2]) \
        and ((linedata[-2] >= linedata[-3]) or (linedata[-2] >= linedata[-4]) or (linedata[-2] >= linedata[-5])):
            return True
        else:
            return False
        '''
    #-----------------------------------------------------------------------------------------------
    def _is_dif_under_dea_back_n_periods(self, periods=14):
        '''
        : why 14
        '''
        dif, dea = self._macd, self._macdsignal
        for i in range(-periods, -1):
            if dif[i] > dea[i]:
                return False
        return True
        '''平均值法会导致交易太频繁
        dif_avg = numpy.average(dif[-periods:])
        dea_avg = numpy.average(dea[-periods:])
        return True if dif_avg < dea_avg else False
        '''
    #-----------------------------------------------------------------------------------------------
    def _is_dif_above_dea_back_n_periods(self, periods=7):
        '''
        : periods = 7, 卖出条件相对12更宽松
        '''
        dif, dea = self._macd, self._macdsignal
        for i in range(-periods, -1):
            if dif[i] < dea[i]:
                return False
        return True
        '''
        dif_avg = numpy.average(dif[-periods:])
        dea_avg = numpy.average(dea[-periods:])
        return True if dif_avg > dea_avg else False
        '''
    #-----------------------------------------------------------------------------------------------
    def _is_dea_under_zero_back_n_periods(self, dea, periods=8):
        '''
        : dea是否在0轴下n个周期，加入这个条件使得买入更苛刻
        '''
        for i in range(-periods, -1):
            if dea[i] > 0:
                return False
        return True

    #-----------------------------------------------------------------------------------------------
    def _is_hist_under_zero_back_n_periods(self, periods=8):
        '''
        : masc hist bar 是否在0轴下n个周期
        : 在_is_dea_under_zero_back_n_periods的基础上改进
        '''
        for i in range(-periods, -2):
            if self._macdhist[i] > 0:
                return False
            return True

    #-----------------------------------------------------------------------------------------------
    def _is_lowest_hist(self):
        '''
        : 判断当前柱是否最低
        '''
        index = numpy.argmin(self._macdhist)
        if index == -1 or index == -2:
            return True
        else:
            return False

    #-----------------------------------------------------------------------------------------------
    def _is_highest_hist(self):
        '''
        : 判断当前柱是否最高
        '''
        index = numpy.argmax(self._macdhist)
        if index == -1 or index == -2:
            return True
        else:
            return False

    #-----------------------------------------------------------------------------------------------
    def _is_pre_dif_dea_far_enough(self, distance=0.3):
        '''
        : 判断dif和dea的距离,距离越大表示信号越强
        '''
        dif, dea = self._macd, self._macdsignal
        max_v = abs(dif[-2])
        min_v = abs(dea[-2])
        #swap
        if max_v < min_v:
            max_v = max_v + min_v
            min_v = max_v - min_v
            max_v = max_v - min_v

        result = (max_v - min_v) / max_v
        if result > distance:
            return True
        return False

    #-----------------------------------------------------------------------------------------------
    def _is_golden_cross(self):
        dif, dea = self._macd, self._macdsignal
        return True if(dif[-1] > dea[-1]) and (dif[-3] < dea[-3]) else False

    #-----------------------------------------------------------------------------------------------
    def _is_dead_cross(self):
        dif, dea = self._macd, self._macdsignal
        return True if (dif[-1] < dea[-1]) and (dif[-3] > dea[-3]) else False

    #-----------------------------------------------------------------------------------------------
    def _is_dif_negtive_when_hist_changeing_to_negtive(self):
        '''
        用于买入前判断当最近一次hist又0轴上变成0轴下时,diff是否已经在0轴下, 如果在则返回true
        '''
        dif, hist = self._macd, self._macdhist
        index = -1
        for i in range(-1, -len(hist), -1):
            if hist[i] <= 0:
                continue
            else:
                index = i
                break

        if dif[index] < 0:
            return True
        else:
            return False
    #-----------------------------------------------------------------------------------------------
    def _is_long_price_under_highest_price_percent(self, long_price):
        '''
        : avoid long at first time price down from latest top price
        '''
        #latest_kline = kline
        klen = 73# 47 + 26?
        klen_amend = 47#47 = 26 + 12 + 9
        latest_kline = self._kline[-klen:]
        latest_kline_amend = self._kline[-klen_amend:]
        highest_price, highest_index = self._get_highest_price_from_kline(latest_kline)
        highest_price_amend, highest_index_amend = self._get_highest_price_from_kline(latest_kline_amend)
        '''
        :修正双头: 例如btc 2017-08-08 22:05 5min不应该买进,最高点应该修正到20：05的233220
        :而非 17:05的23372.5
        '''
        distance = klen - highest_index - (klen_amend - highest_index_amend)
        if highest_price > highest_price_amend and abs(distance) >= 26:
            '''
            :if difference between the two highest less than 0.005%,
            :and they far enough(26 periods?), then amend highest_index
            :--------------H-------------------------------a-----------------------klen
            :                                     ---------h-----------------------klen_amend
            :index of a = klen - (klen_amend - index of h)
            '''
            if highest_price_amend >= (highest_price * 0.995):
                highest_index = klen - (klen_amend - highest_index_amend)
        #:if highest price far enough
        if klen - highest_index > 21:# 12 + 9?
            #当long_price >= highest_price时,认为是在创新高,买入
            if long_price >= highest_price:
                return True
                #: return True run into problem: reason: ltc 3min long at 2017-08-08 13:48:24
                #return False
            else:
                percent = self._config["long_price_down_ratio"]
                diff = highest_price * (1 - percent)
                if long_price <= diff:
                    return True
                else:
                    return False
        else:
            #if too close to hightest price, do NOT long
            return False

    def _is_long_price_under_highest_price_percent2(self, long_price):
        '''
        : use EMA slow as highest price instead, this is out of EMA avg price make more sense than absolute highest price
        '''
        highest_price, index_negtive = self._get_last_ema_dead_cross_avg_price(5, 30)
        if abs(index_negtive) < 21: # 12 + 9?
            return False
        else:
            #当long_price >= highest_price时,认为是在创新高,买入
            if long_price >= highest_price:
                return True
            else:
                percent = self._config["long_price_down_ratio"]
                diff = highest_price * (1 - percent)
                #: if negtive hist under zero enough
                ishuzbnp = self._is_hist_under_zero_back_n_periods(30)
                if long_price <= diff or ishuzbnp:
                    return True
                else:
                    return False
    #-----------------------------------------------------------------------------------------------
    def _is_in_give_up_long_counting(self, kline):
        '''
        : from highest price, give up some times long chance, to skip price dropping relay
        '''
        latest_kline = kline[-60:]
        highest_price, highest_index = self._get_highest_price_from_kline(latest_kline)
        if self._pre_highest_price != highest_price:
            self._pre_highest_price = highest_price
            self._give_up_long_count_down = self._config['give_up_long_count_down']

        if self._give_up_long_count_down > 0:
            print('\tgive up long count down %(gucd)s' %{'gucd': self._give_up_long_count_down})
            self._give_up_long_count_down -= 1
            return True
        else:
            return False
    #-----------------------------------------------------------------------------------------------
    def _is_in_stop_loss_counting(self):
        #if stop loss happend beofre, skip some long times
        if self._stop_loss_count_down > 0:
            print('\tstop loss count down: %(slcd)s' %{'slcd': self._stop_loss_count_down})
            self._stop_loss_count_down -= 1
            return True
        else:
            return False
    #-----------------------------------------------------------------------------------------------
    def _is_dif_above_zero_back_n_periods(self, periods=6):
        '''
        short:
        判断dif是否已经在0轴上方n个周期, 避免假摔
        '''
        if self._macd[-periods] > 0:
            return True
        else:
            return False
    #----------------------------------------------------------------------------------------------
    def _is_reasonalbe_short_price(self, short_price, avg_long_price):
        '''
        : 有一个合理的涨幅才卖, 至少能cover交易费用0.4%
        '''
        if short_price <= avg_long_price:
            return False
        stop_profit_ratio = self._config['stop_profit_ratio']
        if short_price < avg_long_price * (1 + stop_profit_ratio):
            return False
        else:
            return True
    #----------------------------------------------------------------------------------------------
    def _is_hist_close_to_zero_for_n_periods(self, periods=9):
        '''
        : if avg hist almost close to zero for long time(the hist bar hight is below 15% of highest bar hight), do NOT long
        '''
        lowest_hist = abs(min(self._macdhist))
        sum_hist = 0
        for i in range(-periods, -1):
            sum_hist += self._macdhist[i]

        avg_hist = abs(sum_hist) / periods
        if avg_hist / lowest_hist < 0.15:
            return True
        else:
            return False
    
    def _is_volumn_up_sharply(self, kline, quick_periods, slow_periods):
        '''
        : volumn up sharply, and quick ema above slow ema, and close bigger than open
        : this is not verified yet??????
        '''
        close_list = self._get_close_from_kline()
        close = numpy.array(close_list)
        ema_quick = talib.EMA(close, quick_periods)
        ema_slow = talib.EMA(close, slow_periods)
        volumns = list(map(lambda x: x[5], kline))
        avg = numpy.average(volumns[-31:-1])
        lastest_candle = kline[-1]
        if (volumns[-1] > avg * 6) and ema_quick[-1] > ema_slow[-1] and lastest_candle[4] > lastest_candle[1]:
            return True
        else:
            return False
    #----------------------------------------------------------------------------------------------
    def _get_price_vibrate_rate(self, periods=12):
        """
        :0.001
        """
        closes = self._get_close_from_kline()[-periods:]
        opens = self._get_open_from_kline()[-periods:]
        close_avg = abs(numpy.average(closes))
        open_avg = abs(numpy.average(opens))
        max_v = max(close_avg, open_avg)
        diff = abs(close_avg - open_avg)
        return diff / max_v
    #--------------------------------HELPER-------------------------------------------------------
    def _get_highest_price_from_kline(self, latest_kline):
        '''
        : 2017-08-05: change from highest to close
        '''
        high_arr = list(map(lambda x: x[4], latest_kline))
        return max(high_arr), numpy.argmax(high_arr)

    def _get_last_ema_dead_cross_avg_price(self, quick_periods, slow_periods):
        '''
        : return the slow ema value and index when EMA dead cross
        '''
        close_list = self._get_close_from_kline()
        close = numpy.array(close_list)
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
