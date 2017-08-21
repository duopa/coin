'''
'''
import threading
import time
import json
import traceback
from datetime import datetime, timedelta
from strategy import MacdStrategy
from okcoin.OkcoinSpotAPI import OKCoinSpot
from .key import api_key, secret_key
from .config import url_cn, config_3min, config_5min
from common import Logger

class CancelOrderThread(threading.Thread):
    '''
    '''
    def __init__(self, symbol, frequency):
        threading.Thread.__init__(self)        
        self._apikey = api_key
        self._secretkey = secret_key
        self._symbol = symbol
        self._frequency = frequency
        self._okcoin_spot = OKCoinSpot(url_cn, self._apikey, self._secretkey)
        self._logger = Logger('c:/logs/cancelorder', symbol)
        self.daemon = True

    def run(self):
        while 1 == 1:
            try:
                time.sleep(self._frequency)
                self._cancel_hanging_order()
            except:
                tb = traceback.format_exc()
                self._logger.log(tb)

    def _cancel_hanging_order(self):
        orderhistory = json.loads(self._okcoin_spot.order_history(self._symbol, '0', '1', 2))
        if orderhistory['result'] and int(orderhistory['total']) > 0:
            orders = orderhistory['orders']
            for i in range(0, len(orders)):
                create_time = datetime.fromtimestamp(int(orders[i]['create_time']))
                #: if not filled in 120 snds
                offset = datetime.now() - timedelta(seconds=120)
                if create_time < offset:
                    order_id = orders[i]['order_id']
                    result = self._okcoin_spot.cancel_order(self._symbol, order_id)
                    if result['result']:
                        self._logger.log('order {0} cancelled successfully'.format(order_id))
                    else:
                        self._logger.log('order {0} FAILED'.format(order_id))
                        self._logger.log(result)
            '''
            order_ids =','.join(list(map(lambda x: x['order_id'], orders)))
            if order_ids:
                self._okcoin_spot.cancel_order(self._symbol, order_ids)
            '''
