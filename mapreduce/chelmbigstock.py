#!/usr/bin/env python

'''
See if future fluctuations of stock price can be predicted
from the data set prepared by MapReduce code

Mar 1, 2015
@author Hideki Ikeda
'''

class LearningData(object):
    '''
    Stores stock data
    Attributes:
        X : 2D array of feature sets
        y : Array of target values
        m : number of features
        n : number of data sets
    '''

    def __init__(self):
        self._X = []
        self._y = []

    def _add_row(self, row_data):
        if len(self._X) != 0:
            if len(self._X[0]) != len(row_data) - 1:
                raise ValueError('Number of features mismatch')
        self._X.append(row_data[:-1])
        self._y.append(row_data[-1])

    @property
    def X(self):
        # for safety, I must return a copy of _X
        # but I take performance here
        return self._X

    @property
    def y(self):
        # for safety, I must return a copy of _y
        # but I take performance here
        return self._y

    @property
    def m(self):
        return len(self._X[0])

    @property
    def n(self):
        return len(self._y)


def stockDataFactory(fn_data):
    '''
    Read the ouput from Reducer and returns the stock data
    Artument:
        fn_data : file names of the reducer output;
                  Can be a string or a list of strings
    Return:
        Tuple of stock data: (train, CV, test)
    '''
    if isinstance(fn_data, basestring):
        fn_data = [fn_data]

    tr = LearningData()
    cv = LearningData()
    te = LearningData()

    for fn in fn_data:
        with open(fn, 'r') as fh:
            for line in fh:
                data_type, values = line.strip().split('\t')
                if data_type == 'TR':
                    stock = tr
                elif data_type == 'CV':
                    stock = cv
                elif data_type == 'TE':
                    stock = te
                else:
                    raise ValueError('Data error in {}: Unknonw data type "{}"'
                            .format(fn, data_type))

                values = [ float(v) for v in values.split(',') ]
                stock._add_row(values)

    return (tr, cv, te)


if __name__ == '__main__':
    print 'Not implemented yet'
