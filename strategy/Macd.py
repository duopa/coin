"""
"""
import numpy
import talib

class MacdStrategy:
    def __init__(self):
        #self.__kline = kline
        pass

    #execute strategy
    def execute(self, kline):
        print('Macd executing')
        close_list = self._get_close_from_kline(kline)
        close = numpy.array(close_list)
        #dif, dea, diff - dea?
        macd, macdsignal, macdhist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        if self._long_signal(macd, macdsignal):
            return 'l'
        elif self._short_signal(macd, macdsignal):
            return 's'
        else:
            return ''        
        #print(macd)
        #print(macdsignal)
        #print(macdhist)
    
    #long signal
    def _long_signal(self, macd, macdsignal):
        return (macd[-1] < 0) and (macdsignal[-1] < 0) \
        and self._is_slope_changing_to_positive(macd) \
        and self._is_dif_under_dea_back_n_periods(macd, macdsignal)

    #short signal
    def _short_signal(self, macd, macdsignal):
        return self._is_slope_changing_to_negtive(macd) \
        and self._is_dif_above_dea_back_n_periods(macd, macdsignal)

    #get close price from kline
    def _get_close_from_kline(self, kline):
        close = []
        for arr in kline:
            close.append(arr[4])
        return close

    #whether slope of dif line head up
    def _is_slope_changing_to_positive(self, linedata):
        if (linedata[-1] >= linedata[-2]) \
        and ((linedata[-2] <= linedata[-3]) or (linedata[-2] <= linedata[-4]) or (linedata[-2] < linedata[-5])):
            return True
        else:
            return False

    #whether slope of diff line head down
    def _is_slope_changing_to_negtive(self, linedata):
        if (linedata[-1] <= linedata[-2]) \
        and ((linedata[-2] >= linedata[-3]) or (linedata[-2] >= linedata[-4]) or (linedata[-2] >= linedata[-5])):
            return True
        else:
            return False

    #
    def _is_dif_under_dea_back_n_periods(self, dif, dea, periods = 12):        
        for i in range(-periods, -1):
            if dif[i] > dea[i]:
                return False
        return True
        '''平均值法会导致交易太频繁
        dif_avg = numpy.average(dif[-periods:])
        dea_avg = numpy.average(dea[-periods:])
        return True if dif_avg < dea_avg else False
        '''

    # periods = 8, 卖出条件相对12更宽松
    def _is_dif_above_dea_back_n_periods(self, dif, dea, periods = 8):
        for i in range(-periods, -1):
            if dif[i] < dea[i]:
                return False
        return True
        '''
        dif_avg = numpy.average(dif[-periods:])
        dea_avg = numpy.average(dea[-periods:])
        return True if dif_avg > dea_avg else False
        '''

    # golden cross
    def _is_golden_cross(self, dif, dea):
        return True if (dif[-1] > dea [-1]) and (dif[-3] < dea[-3]) else False

    # dead cross
    def _is_dead_cross(self, dif, dea):
        return True if (dif[-1] < dea[-1]) and (dif[-3] > dea[-3]) else False

    def _stop_loss(self):
        pass