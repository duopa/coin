import numpy
from common import Logger


''' test get min and max of array and numpy array
arr = [1, -1, 2, 3, 6, 3, 2]

narr = numpy.array(arr)
print(numpy.argmax(narr))
print(numpy.argmin(narr))

min = numpy.min(arr)
max = numpy.max(arr)

print(arr.index(min))
print(arr.index(max))
print(len(arr) - arr.index(max))
'''

logger = Logger('c:/logs', 'btc_cny')
logger.log('test %(test)s' %{'test':'a test log'})
