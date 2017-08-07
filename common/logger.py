
import logging
import logging.config
import os

class Logger:
    '''
    '''
    def __init__(self, path, filename):
        '''
        path = os.path.dirname(os.path.realpath(__file__))
        logging.config.fileConfig(path + '/logging.conf')    
        self._logger = logging.getLogger('root')
        '''
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s", "%Y-%m-%d %H:%M:%S")
        handler = logging.handlers.TimedRotatingFileHandler("{0}/{1}.log".format(path, filename), 'midnight', 1, 15)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def log(self, msg):
        self._logger.info(msg)
