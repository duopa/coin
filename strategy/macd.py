"""
"""
from datetime import datetime
import numpy
import talib

class MacdStrategy:
    '''
    :
    '''
    def __init__(self, **kwargs):
        #self.__kline = kline
        self._stop_loss_count_down = 0
        self._config = kwargs
        self._pre_highest_price = 0
        self._give_up_long_count_down = 1
    #-----------------------------------------------------------------------------------------------
    #def execute(self, kline, last, long_price, avg_long_price, holding):
    def  execute(self, kline, **kwargs):
        '''
        : execute strategy
        '''
        #now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        #print('at:%(datetime)s MacdStrategy executing' %{'datetime': now})

        last = kwargs['last']
        long_price = kwargs['long_price']
        short_price = kwargs['short_price']
        avg_long_price = kwargs['avg_long_price']
        holding = kwargs['holding']

        if self._should_stop_loss(last, avg_long_price, holding):
            return 'sl'
        elif self._long_signal(kline, long_price):
            return 'l'
        elif self._short_signal(kline, short_price, avg_long_price):
            return 's'
        else:
            return ''
    #-----------------------------------------------------------------------------------------------
    def _long_signal(self, kline, long_price):
        '''
        : long signal
        '''
        #dif, dea, diff - dea?
        macd, macdsignal, macdhist = self._get_macd(kline)
        result = (macd[-1] < 0) and (macdsignal[-1] < 0) \
        and self._is_slope_changing_to_positive(macd) \
        and self._is_hist_under_zero_back_n_periods(macdhist, 8) \
        and not self._is_hist_close_to_zero_for_n_periods(macdhist) \
        and self._is_long_price_under_highest_price_percent2(kline, long_price, 0.015) \
        and (self._is_dif_under_dea_back_n_periods(macd, macdsignal) or self._is_lowest_hist(macdhist) or self._is_pre_dif_dea_far_enough(macd, macdsignal))

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
    def _short_signal(self, kline, short_price, avg_long_price):
        '''
        : short signal
        '''
        if not self._is_reasonalbe_short_price(short_price, avg_long_price):
            return False
        #dif, dea, diff - dea?
        macd, macdsignal, macdhist = self._get_macd(kline)
        isslopechangingtonegtive = self._is_slope_changing_to_negtive(macd)
        isdifabovedeabacknperiods = self._is_dif_above_dea_back_n_periods(macd, macdsignal, 8)
        ishighesthist = self._is_highest_hist(macdhist)
        ispredifdeafarenough = self._is_pre_dif_dea_far_enough(macd, macdsignal)
        dif_above_zero_back_n_periods = self._is_dif_above_zero_back_n_periods(macd, 6)
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
    def _is_slope_changing_to_positive(self, linedata):
        '''
        : whether slope of dif line head up
        : 找一个更好的算法确定方向改变
        '''
        #最低点法判定方向改变向上
        if len(linedata) < 12:
            return False
        temp = linedata[-12:]
        #min = numpy.min(temp)
        #index = temp.index(min)
        index = numpy.argmin(temp)
        #会导致交易两次
        #if(2 <= len(temp) - index <= 3):
        if len(temp) - index == 3:#最低点在倒数第三个表面方向向上(可能要调整)
            return True
        else:
            return False
        '''
        if (linedata[-1] >= linedata[-2]) \
        and ((linedata[-2] <= linedata[-3]) or (linedata[-2] <= linedata[-4]) or (linedata[-2] < linedata[-5])):
            return True
        else:
            return False
        '''
    #-----------------------------------------------------------------------------------------------
    def _is_slope_changing_to_negtive(self, linedata):
        '''
        : whether slope of diff line heading down
        '''
        #最高点法判定方向改变向下
        if len(linedata) < 12:
            return False
        temp = linedata[-12:]
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
    def _is_dif_under_dea_back_n_periods(self, dif, dea, periods=14):
        '''
        : why 14
        '''
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
    def _is_dif_above_dea_back_n_periods(self, dif, dea, periods=7):
        '''
        : periods = 7, 卖出条件相对12更宽松
        '''
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
    def _is_hist_under_zero_back_n_periods(self, macdhist, periods=8):
        '''
        : masc hist bar 是否在0轴下n个周期
        : 在_is_dea_under_zero_back_n_periods的基础上改进
        '''
        for i in range(-periods, -2):
            if macdhist[i] > 0:
                return False
            return True

    #-----------------------------------------------------------------------------------------------
    def _is_lowest_hist(self, macdhist):
        '''
        : 判断当前柱是否最低
        '''
        index = numpy.argmin(macdhist)
        if index == -1 or index == -2:
            return True
        else:
            return False

    #-----------------------------------------------------------------------------------------------
    def _is_highest_hist(self, macdhist):
        '''
        : 判断当前柱是否最高
        '''
        index = numpy.argmax(macdhist)
        if index == -1 or index == -2:
            return True
        else:
            return False

    #-----------------------------------------------------------------------------------------------
    def _is_pre_dif_dea_far_enough(self, dif, dea, distance=0.3):
        '''
        : 判断dif和dea的距离,距离越大表示信号越强
        '''
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
    def _is_golden_cross(self, dif, dea):
        return True if(dif[-1] > dea[-1]) and (dif[-3] < dea[-3]) else False

    #-----------------------------------------------------------------------------------------------
    def _is_dead_cross(self, dif, dea):
        return True if (dif[-1] < dea[-1]) and (dif[-3] > dea[-3]) else False

    #-----------------------------------------------------------------------------------------------
    def _is_dif_negtive_when_hist_changeing_to_negtive(self, dif, hist):
        '''
        用于买入前判断当最近一次hist又0轴上变成0轴下时,diff是否已经在0轴下, 如果在则返回true
        '''
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
    def _is_long_price_under_highest_price_percent(self, kline, long_price, percent=0.01):
        '''
        : avoid long at first time price down from latest top price
        '''
        #latest_kline = kline
        klen = 73# 47 + 26?
        klen_amend = 47#47 = 26 + 12 + 9
        latest_kline = kline[-klen:]
        latest_kline_amend= kline[-klen_amend:]
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
        if klen - highest_index > 35:# 26 + 9?
            #当long_price >= highest_price时,认为是在创新高,买入
            if long_price >= highest_price:
                return True
                #: return True run into problem: reason: ltc 3min long at 2017-08-08 13:48:24
                #return False
            else:
                diff = highest_price * (1-percent)
                if long_price <= diff:
                    return True
                else:
                    return False
        else:
            #if too close to hightest price, do NOT long
            return False

    def _is_long_price_under_highest_price_percent2(self, kline, long_price, percent=0.01):
        '''
        : use EMA slow as highest price instead, this is out of EMA avg price make more sense than absolute highest price
        '''
        highest_price, index_negtive = self._get_last_ema_dead_cross_avg_price(kline, 5, 30)
        if abs(index_negtive) < 21: # 12 + 9?
            return False
        else:
            #当long_price >= highest_price时,认为是在创新高,买入
            if long_price >= highest_price:
                return True
            else:
                diff = highest_price * (1-percent)
                if long_price <= diff:
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
    def _is_dif_above_zero_back_n_periods(self, dif, periods=6):
        '''
        short:
        判断dif是否已经在0轴上方n个周期, 避免假摔
        '''
        if dif[-periods] > 0:
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
    def _is_hist_close_to_zero_for_n_periods(self, hist, periods=9):
        '''
        : if avg hist almost close to zero for long time(the hist bar hight is below 15% of highest bar hight), do NOT long
        '''
        lowest_hist = abs(min(hist))
        sum_hist = 0
        for i in range(-periods, -1):
            sum_hist += hist[i]

        avg_hist = abs(sum_hist) / periods
        if avg_hist / lowest_hist < 0.15:
            return True
        else:
            return False
    
    #----------------------------------------------------------------------------------------------
    def _get_price_vibrate_rate(self, kline, periods=12):
        """
        :0.001
        """
        closes = self._get_close_from_kline(kline)[-periods:]
        opens = self._get_open_from_kline(kline)[-periods:]
        close_avg = abs(numpy.average(closes))
        open_avg = abs(numpy.average(opens))
        max_v = max(close_avg, open_avg)
        diff = abs(close_avg - open_avg)
        return diff / max_v
    #--------------------------------helper-------------------------------------------------------
    def _get_macd(self, kline):
        close_list = self._get_close_from_kline(kline)
        close = numpy.array(close_list)
        #dif, dea, diff - dea?
        return talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

    ### get close price from kline
    def _get_close_from_kline(self, kline):
        close = []
        for arr in kline:
            close.append(arr[4])
        return close

    def _get_open_from_kline(self, kline):
        opens = []
        for arr in kline:
            opens.append(arr[1])
        return opens
    ###
    def _get_highest_price_from_kline(self, kline):
        '''
        : 2017-08-05: change from highest to close
        '''
        high_arr = list(map(lambda x: x[4], kline))
        return max(high_arr), numpy.argmax(high_arr)

    def _get_last_ema_dead_cross_avg_price(self, kline, quick_periods, slow_periods):
        '''
        : return the slow ema value and index when EMA dead cross
        '''
        close_list = self._get_close_from_kline(kline)
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
