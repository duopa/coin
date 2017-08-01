"""
"""
import numpy
import talib
from datetime import datetime

class MacdStrategy:
    def __init__(self):
        #self.__kline = kline
        pass

    #execute strategy
    def execute(self, kline, ticker, long_price, avg_long_price):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print('at:%(datetime)s MacdStrategy executing' %{'datetime': now})
        highest_price = self._get_highest_price_from_kline(kline)
        close_list = self._get_close_from_kline(kline)
        close = numpy.array(close_list)

        #dif, dea, diff - dea?
        macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        if self._should_stop_loss(ticker, avg_long_price):
            return 'sl'
        elif self._long_signal(macd, macdsignal, macdhist, long_price, highest_price):
            return 'l'
        elif self._short_signal(macd, macdsignal, macdhist):
            return 's'
        else:
            return ''
        #print(macd)
        #print(macdsignal)
        #print(macdhist)

    ### long signal
    def _long_signal(self, macd, macdsignal, macdhist, long_price, highest_price):
        return (macd[-1] < 0) and (macdsignal[-1] < 0) \
        and self._is_slope_changing_to_positive(macd) \
        and self._is_hist_under_zero_back_n_periods(macdhist, 8) \
        and self._is_long_price_under_highest_price_percent(long_price, highest_price) \
        and (self._is_dif_under_dea_back_n_periods(macd, macdsignal) or self._is_lowest_hist(macdhist) or self._is_pre_dif_dea_far_enough(macd, macdsignal))

    #### short signal
    def _short_signal(self, macd, macdsignal, macdhist):
        isslopechangingtonegtive = self._is_slope_changing_to_negtive(macd)
        isdifabovedeabacknperiods = self._is_dif_above_dea_back_n_periods(macd, macdsignal, 8)
        ishighesthist = self._is_highest_hist(macdhist)
        ispredifdeafarenough = self._is_pre_dif_dea_far_enough(macd, macdsignal)
        '''
        try:
            print('\tshot_signal: %(a)s %(b)s %(c)s %(d)s' %{'a': isslopechangingtonegtive, 'b': isdifabovedeabacknperiods, 'c': ishighesthist, 'd':ispredifdeafarenough})
        except:
            pass
        '''
        return isslopechangingtonegtive and (isdifabovedeabacknperiods or ishighesthist or ispredifdeafarenough)

    ### top loss signal
    def _should_stop_loss(self, ticker, avglongprice):
        last = float(ticker['ticker']['last'])
        if last < avglongprice:
            loss = (avglongprice - last)/avglongprice
            if loss >= 0.02:
                return True
        return False

    ### whether slope of dif line head up
    def _is_slope_changing_to_positive(self, linedata):
        '''
        找一个更好的算法确定方向改变
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

    #whether slope of diff line head down
    def _is_slope_changing_to_negtive(self, linedata):
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

    # why 14
    def _is_dif_under_dea_back_n_periods(self, dif, dea, periods=14):
        for i in range(-periods, -1):
            if dif[i] > dea[i]:
                return False
        return True
        '''平均值法会导致交易太频繁
        dif_avg = numpy.average(dif[-periods:])
        dea_avg = numpy.average(dea[-periods:])
        return True if dif_avg < dea_avg else False
        '''

    # periods = 7, 卖出条件相对12更宽松
    def _is_dif_above_dea_back_n_periods(self, dif, dea, periods=7):
        for i in range(-periods, -1):
            if dif[i] < dea[i]:
                return False
        return True
        '''
        dif_avg = numpy.average(dif[-periods:])
        dea_avg = numpy.average(dea[-periods:])
        return True if dif_avg > dea_avg else False
        '''

    # dea是否在0轴下n个周期，加入这个条件使得买入更苛刻
    def _is_dea_under_zero_back_n_periods(self, dea, periods = 8):
        for i in range(-periods, -1):
            if dea[i] > 0:
                return False
        return True

    # masc hist bar 是否在0轴下n个周期
    def _is_hist_under_zero_back_n_periods(self, macdhist, periods = 8):
        '''
        在_is_dea_under_zero_back_n_periods的基础上改进
        '''
        for i in range(-periods, -1):
            if macdhist[i] > 0:
                return False
            return True

    # 判断当前柱是否最低
    def _is_lowest_hist(self, macdhist):
        index = numpy.argmin(macdhist)
        if index == -1 or index == -2:
            return True
        else:
            return False

    # 判断当前柱是否最高
    def _is_highest_hist(self, macdhist):
        index = numpy.argmax(macdhist)
        if index == -1 or index == -2:
            return True
        else:
            return False

    # 判断dif和dea的距离,距离越大表示信号越强
    def _is_pre_dif_dea_far_enough(self, dif, dea, distance=0.3):
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

    # golden cross
    def _is_golden_cross(self, dif, dea):
        return True if (dif[-1] > dea [-1]) and (dif[-3] < dea[-3]) else False

    # dead cross
    def _is_dead_cross(self, dif, dea):
        return True if (dif[-1] < dea[-1]) and (dif[-3] > dea[-3]) else False

    ###
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

    ###
    def _is_long_price_under_highest_price_percent(self, long_price, highest_price, percent=0.05):
        '''
        只有买入价在最高价以下 percent%时才买入，防止持续下跌的第一次反弹就买入，此时买在半山腰
        '''
        #当long_price >= highest_price时,认为是在创新高,买入
        if long_price >= highest_price:
            return True
        else:
            diff = highest_price * (1-percent)
            if long_price > diff:
                return False
            else:
                return True

    ###--------------------------------helper-------------------------------    
    ### get close price from kline
    def _get_close_from_kline(self, kline):
        close = []
        for arr in kline:
            close.append(arr[4])
        return close

    ###
    def _get_highest_price_from_kline(self, kline):
        high_arr = map(lambda x: x[2], kline)
        return max(high_arr)
