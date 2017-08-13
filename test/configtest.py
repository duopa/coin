import sys
import os
import json
sys.path.append(os.path.abspath(os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir)))
from okcoin.config import *

path = os.path.abspath(os.path.join(os.path.realpath(os.path.dirname(__file__)), os.pardir))
print(path)
config3min = config_3min
print(config3min)
print(config3min["short_ratio"][2])