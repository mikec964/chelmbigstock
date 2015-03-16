#!/usr/bin/env python

'''
See if future fluctuations of stock price can be predicted
from the data set prepared by MapReduce code
This script needs numpy, scikit-learn

Mar 1, 2015
@author Hideki Ikeda
'''

from __future__ import print_function

import sys
import argparse
import numpy as np
from sklearn import linear_model
from scipy.stats import anderson
from matplotlib import pyplot as plt


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
                # raise ValueError('Number of features mismatch')
                print('Number of features mismatch', file=sys.stderr)
                return
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


def learn(training_data, cv_data):
    """
    I copied this function from Andy Webber's code in
    chelmbigstock/chelmbigstock/chelmbigstock.py almost as is,
    though I made some cosmetic changes.

    This function does the actual training. It takes in training data
    and cross validation data and returns the model and optimal
    regularization parameter
    """
    
    # Setting guesses for minimum and maximum values of regularization parameter
    # then find the value of parameter that minimizes error on cross validation
    # data. If local minimum is found the return this model. If not,
    # extend minimum or maximum appropriately and repeat
    alpha_min = 0.01
    alpha_max = 0.2
    regularization_flag = 1 # To set 1 until local minimum is found
    regularization_param = 0
    
    while regularization_flag != 0:
        regularization_param, regularization_flag = set_reg_param(
                training_data, cv_data, alpha_min, alpha_max)
        if regularization_flag == -1:
            # The local minimum is at point less than alpha_min
            alpha_min = alpha_min * 0.3
        if regularization_flag == 1:
            # The local minimum is at point greater then alpha_max
            alpha_max = alpha_max * 3
            
    clf = linear_model.Ridge (alpha=regularization_param, fit_intercept=False)
    clf.fit(training_data.X, training_data.y)
    return clf, regularization_param


def set_reg_param(training_data, cv_data, alpha_min, alpha_max):
    """
    I copied this function from Andy Webber's code in
    chelmbigstock/chelmbigstock/chelmbigstock.py almost as is,
    though I made some cosmetic changes.

    This function does a linear regression with regularization for training_data
    then tests prediction for training_data and cv_data over a range of
    regularization parameters. If a local minimum is found it returns the parameter
    and a 0 to indicate it is complete. If minimum it below alpha_min it returns -1
    for flag. If it is above alpha_max, it returns 1 for flag.
    """
        
    f = open('alpha.txt', 'w')
    
    alph = alpha_min
    
    # the value of alpha in our range that gives minimum for cv data
    min_alpha = alpha_min

    # Learning is not generally done at alpha_min, this tracks larget alpha
    alpha_largest = alpha_min
    while alph < alpha_max:
        # Learn for this parameter
        clf = linear_model.Ridge (alpha=alph, fit_intercept=False)
        clf.fit(training_data.X, training_data.y)
        
        # Get prediction for this parameter
        predict_data = clf.predict(training_data.X)
        predict_cv = clf.predict(cv_data.X)
        
        # Caculate the differences from actual data for training and cv data
        diff_training = (1.0/training_data.m) * np.linalg.norm(predict_data - training_data.y)
        diff_cv = (1.0/cv_data.m) * np.linalg.norm(predict_cv - cv_data.y)
        
        # Write out the values for plotting.
        # Do appropriate work to determine min_val_alpha
        f.write(str(alph) +  " " + str(diff_training) + " " + str(diff_cv) +  "\n")
        if alph == alpha_min:
            min_diff = diff_cv # Just setting default value for first value of alph 
            min_alpha = alpha_min
        if diff_cv < min_diff:
            """ We have a new minimum so value and alph must be recored """
            min_diff = diff_cv
            min_alpha = alph
        alpha_largest = alph # Keep track of largest alpha used
        alph = alph * 1.5 # increment alph
    f.close()
            
    """ Loop is now complete. If min_value_alpha is not alpha_min or alpha_max, return flag of 0
            else return -1 or 1 so min or max can be adjusted and loop completed again """
    if abs(min_alpha - alpha_min) < alpha_min/10.0:
        flag = -1 # Local minimum is less than alpha_min so return -1 
    elif abs(min_alpha - alpha_largest) < alpha_min/10.0:
        flag = 1 # Local minimum is greater than alpha_max so return 1 
    else:
        flag = 0 # Local minimum is in range so return 0 
        
    return min_alpha, flag


def save_as_csv(training_data, cv_data,
        fn_TRX = 'training_X.csv', fn_TRy = 'training_y.csv',
        fn_CVX = 'CV_X.csv', fn_CVy = 'CV_y.csv'):
    '''
    This function outputs the data in csv form so it can be examined in Matlab
    '''
    
    with open(fn_TRX,'w') as f:
        for line in training_data.X:
            x_str = ','.join(line)
            print(x_str)
            print(x_str, file=f)
    
    with open(fn_TRy,'w') as f:
        y_str = ','.join(str(y) for y in training_data.y)
        print(y_str, file=f)
    
    with open(fn_CVX,'w') as f:
        for line in cv_data.X:
            x_str = ','.join(line)
            print(x_str)
            print(x_str, file=f)
    
    with open(fn_CVy,'w') as f:
        y_str = ','.join(str(y) for y in cv_data.y)
        print(y_str, file=f)
    

def execute(training_data, cv_data, test_data): 
    """
    execute is the function where each run is done. main sets parameters
    then calls execute
    """
    
    clf, regularization_parameter = learn(training_data, cv_data)
    
    # do an Anderson Darling test on the data to determine if it is a normal fit
    A2, sig, crit = anderson(test_data.y, dist = 'norm')
    
    test_mn = np.mean(test_data.y)
    test_sd = np.std(test_data.y)
    
    
    predict_data = clf.predict(test_data.X)
    difference = predict_data - test_data.y
    diff_mn = np.mean(difference)
    diff_sd = np.std(difference)

    print("the value for A2 is ", A2)
    print("The mean and standard deviation of the test data are ",
            test_mn, test_sd)
    print("The mean and standard deviation of the difference are ",
            diff_mn, diff_sd)

    # make plot
    bin_max = max(max(test_data.y), max(predict_data))
    bin_min = min(min(test_data.y), min(predict_data))

    fig = plt.figure()
    ax0 = fig.add_subplot(221)
    ax1 = fig.add_subplot(222, sharey=ax0)
    ax2 = fig.add_subplot(212)

    # test data
    count, bins, ignored = ax0.hist(test_data.y, 30, (bin_min, bin_max), color='r')
    ax0.set_title('test data')
    # prediction
    ax1.hist(predict_data, bins)
    ax1.set_title('prediction')

    # compare per stock
    ind = np.arange(len(test_data.y))
    width = 0.35
    rects1 = ax2.bar(ind, test_data.y, width, color='r')
    rects2 = ax2.bar(ind+width, predict_data, width, color='b')
    ax2.set_title('Comparison per stock')

    # draw the plot
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stock analysis')
    parser.add_argument('data_file', help='Stock price data from the reducer')
    parser.add_argument('-c', '--save_csv', action='store_true', dest='save_csv',
            help='Save the training and CV data in the csv format')
    opt = parser.parse_args()

    training_data, cv_data, test_data = stockDataFactory(opt.data_file)
    if opt.save_csv:
        save_as_csv(training_data, cv_data)

    execute(training_data, cv_data, test_data)
