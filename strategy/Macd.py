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
    def execute(self, kline):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print('at:%(datetime)s MacdStrategy executing' %{'datetime': now})
        close_list = self._get_close_from_kline(kline)
        close = numpy.array(close_list)
        #dif, dea, diff - dea?
        macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        if self._long_signal(macd, macdsignal, macdhist):
            return 'l'
        elif self._short_signal(macd, macdsignal, macdhist):
            return 's'
        else:
            return ''
        #print(macd)
        #print(macdsignal)
        #print(macdhist)
    
    #long signal
    def _long_signal(self, macd, macdsignal, macdhist):
        return (macd[-1] < 0) and (macdsignal[-1] < 0) \
        and self._is_slope_changing_to_positive(macd) \
        and (self._is_dif_under_dea_back_n_periods(macd, macdsignal) or self._is_lowest_hist(macdhist) or self._is_pre_dif_dea_far_enough(macd, macdsignal))

    #short signal
    def _short_signal(self, macd, macdsignal, macdhist):
        return self._is_slope_changing_to_negtive(macd) \
        and (self._is_dif_above_dea_back_n_periods(macd, macdsignal) or self._is_highest_hist(macdhist))

    #get close price from kline
    def _get_close_from_kline(self, kline):
        close = []
        for arr in kline:
            close.append(arr[4])
        return close

    #whether slope of dif line head up
    def _is_slope_changing_to_positive(self, linedata):
        #最低点法判定方向改变向上
        if(len(linedata) < 12):
            return False
        temp = linedata[-12:]
        #min = numpy.min(temp)
        #index = temp.index(min)
        index = numpy.argmin(temp)
        #会导致交易两次
        #if(2 <= len(temp) - index <= 3):
        if(len(temp) - index == 2):
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
        if(len(linedata) < 12):
            return False
        temp = linedata[-12:]
        #max = numpy.min(temp)
        #index = temp.index(max)
        index = numpy.argmax(temp)
        #会导致交易两次
        #if(2 <= len(temp) - index <= 3):
        if(len(temp) - index == 2):
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
    def _is_dif_under_dea_back_n_periods(self, dif, dea, periods = 14):        
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
    def _is_dif_above_dea_back_n_periods(self, dif, dea, periods = 7):
        for i in range(-periods, -1):
            if dif[i] < dea[i]:
                return False
        return True
        '''
        dif_avg = numpy.average(dif[-periods:])
        dea_avg = numpy.average(dea[-periods:])
        return True if dif_avg > dea_avg else False
        '''
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

    def _is_pre_dif_dea_far_enough(self, dif, dea):
        max = abs(dif[-2])
        min = abs(dea[-2])
        #swap
        if max < min:
            max = max + min
            min = max - min

        result = (max - min) / max
        if result > 0.3:
            return True
        return False

    # golden cross
    def _is_golden_cross(self, dif, dea):
        return True if (dif[-1] > dea [-1]) and (dif[-3] < dea[-3]) else False

    # dead cross
    def _is_dead_cross(self, dif, dea):
        return True if (dif[-1] < dea[-1]) and (dif[-3] > dea[-3]) else False

    def should_stop_loss(self, ticker, last_long_price):
        last = float(ticker['ticker']['last'])
        if last < last_long_price:
            loss = (last_long_price - last)/last_long_price
            if loss >= 0.02:
                return True
        return False