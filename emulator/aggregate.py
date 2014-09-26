"""
Hadoop stream API emulator for python mapper/reducer
The aggregate reducer module

@Author: Hideki Ikeda
Created: September 26, 2014
"""

import sys


#
# local exceptions
#
class AGGRException(Exception):
    """
    Base class for local exceptions
    """
    pass


class AGGRNoAggregatorError(AGGRException):
    """
    Exception raised when no aggregator found
    """
    def __init__(self, aggregator):
        self.msg = 'No aggregator for {} found'.format(aggregator)


#
# Aggregator definitions
#
class AGGRNull(object):
    """
    The initial dummy aggregator: Does nothing
    """

    def __init__(self):
        pass

    # def append(self, value): never to be called

    def emit(self, emitter):
        pass


class AGGRLongValueSum(object):
    """
    Aggregator to sum up Long values
    """

    def __init__(self):
        self._sum = None

    def append(self, value):
        """
        Parameter:
            value: string to represent integer value. If 'Value' cannot
                   converted to integer value, does nothing
        """
        try:
            value = int(value)
        except ValueError:
            pass    # just ignore
        else:
            self._sum = value if self._sum == None else self._sum + value

    def emit(self, emitter):
        if self._sum != None:
            emitter(self._sum)


#
# aggregator factory
#
def aggregator_factory(aggr_name):
    if not aggr_name in aggregator_factory.aggregators:
        raise AGGRNoAggregatorError(aggr_name)
    return aggregator_factory.aggregators[aggr_name]()

# do not include AGGRNull in the aggregator dictionary as it is meant for
# the initial value
aggregator_factory.aggregators = {
    'LongValueSum':AGGRLongValueSum
    }


#
# main
#
def main():
    aggregator = AGGRNull()
    last_aggre_key = None
    last_key = None

    def emitter(value):
        print '{}\t{}'.format(last_key, value)

    for line in sys.stdin:
        aggre_key, value = line.strip().split('\t', 1)
        if aggre_key != last_aggre_key:
            # if we got a new key, emit the last aggregation and
            # start a new aggregation
            aggregator.emit(emitter)
            last_aggre_key = aggre_key
            aggre_name, last_key = aggre_key.split(':', 1)
            aggregator = aggregator_factory(aggre_name)
        aggregator.append(value)

    # emit the last aggregation
    aggregator.emit(emitter)


if __name__ == '__main__':
    try:
        main()
    except AGGRException:
        ret_code = 1
    else:
        ret_code = 0

    sys.exit(ret_code)
