import logging
import random
import os

class MyFileHandler(logging.FileHandler):
    '''
    : try to custoize filename with coin name
    '''
    def __init__(self,path,fileName,mode):        
        path = "c:/logs/" + fileName
        #os.mkdir(path)
        super(myFileHandler,self).__init__(path, 'a')
        #super(myFileHandler,self).__init__(path+"/"+fileName,mode)