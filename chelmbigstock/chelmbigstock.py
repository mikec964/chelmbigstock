#!/usr/bin/env python3

"""
Code to use stock history to see if future fluctuations can be predicted

@Author: Andy Webber
Created: March 1, 2014
"""
# A python script to learn about stock picking
import sys

from operator import itemgetter

import numpy as np
from sklearn import linear_model
from scipy.stats import anderson

import dateutil
from Stock import Stock
from LearningData import LearningData

def form_data(init_param):
    """ This function constructs the training, testing and cross validation
        objects for the stock market analysis """
    stocks = Stock.read_stocks('../data/stocks_read.txt', init_param.max_stocks)
    stocks_train = []
    stocks_cv = []
    stocks_test = []
    count = 0
    for stock in stocks:
        if count % init_param.cv_factor == 0:
            stocks_train.append(stock)
        else:
            stocks_cv.append(stock)
        count = count + 1
    
    day_history = []
    for i in range(init_param.train_increment, init_param.train_days, init_param.train_increment):
        day_history.append(i)
        
    for date in init_param.reference_dates:
        try:
            training_data
        except NameError:
            training_data = LearningData()
            training_data.construct(stocks_train,[date, day_history, init_param.future_day])
            cv_data = LearningData()
            cv_data.construct(stocks_cv,[date, day_history, init_param.future_day])
        else:
            training_data.append(stocks_train,[date, day_history, init_param.future_day])
            cv_data.append(stocks_cv,[date, day_history, init_param.future_day])
            
    for date in init_param.test_dates:
        try:
            test_data
        except NameError:
            test_data = LearningData()
            test_data.construct(stocks,[date, day_history, init_param.future_day])
        else:
            test_data.append(stocks,[date, day_history, init_param.future_day])
    
    #reference_date = dateutil.days_since_1900('1991-01-01')
    #test_data.construct(stocks,[reference_date, day_history, init_param.future_day])
    
    return training_data, cv_data, test_data

def output(training_data, cv_data):
    " This function outputs the data in csv form so it can be examined in Matlab"
    
    f = open('training_x.txt','w')
    for i in range(0,training_data.m):
        x_str = ','.join(str(x) for x in training_data.X[i])
        print(x_str)
        f.write(x_str + '\n')
    f.close
    
    f = open('training_y.txt','w')
    y_str = ','.join(str(y) for y in training_data.y)
    f.write(y_str)
    f.close
    
    f = open('cv_x.txt','w')
    for i in range(0,cv_data.m):
        x_str = ','.join(str(x) for x in cv_data.X[i])
        print(x_str)
        f.write(x_str + '\n')
    f.close
    
    f = open('cv_y.txt','w')
    y_str = ','.join(str(y) for y in cv_data.y)
    f.write(y_str)
    f.close
    
def learn(training_data, cv_data):
    """ This function does the actual training. It takes in training data
        and cross validation data and returns the model and optimal 
        regularization parameter """
    
    """ Setting guesses for minimum and maximum values of regularization parameter then
        find the value of parameter that minimizes error on cross validation data. If
        local minimum is found the return this model. If not, extend minimum or maximum 
        appropriately and repeat """
    alpha_min = 0.01
    alpha_max = 0.2
    regularization_flag = 1 # To set 1 until local minimum is found
    regularization_param = 0
    
    while regularization_flag != 0:
        regularization_param, regularization_flag = set_reg_param(training_data, cv_data, alpha_min, alpha_max)
        if regularization_flag == -1:
            """ The local minimum is at point less than alpha_min """
            alpha_min = alpha_min * 0.3
        if regularization_flag == 1:
            """ The local minimum is at point greater then alpha_max """
            alpha_max = alpha_max * 3
            
    clf = linear_model.Ridge (alpha=regularization_param, fit_intercept=False)
    clf.fit(training_data.X, training_data.y)
    return clf, regularization_param

def set_reg_param(training_data, cv_data, alpha_min, alpha_max):
    """ This function does a linear regression with regularization for training_data
        then tests prediction for training_data and cv_data over a range of regularization
        parameters. If a local minimum is found it returns the parameter and a 0 to indicate
        it is complete. If minimum it below alpha_min it returns -1 for flag. If it is above
        alpha_max, it returns 1 for flag. """
        
    f = open('alpha.txt', 'w')
    
    alph = alpha_min
    min_alpha = alpha_min # This is the value of alpha in our range that gives minimum for cv data
    alpha_largest = alpha_min # Learning is not generally done at alpha_min, this tracks larget alpha
    while alph < alpha_max:
        """ Learn for this parameter """
        clf = linear_model.Ridge (alpha=alph, fit_intercept=False)
        clf.fit(training_data.X, training_data.y)
        
        """ Get prediction for this parameter """
        predict_data = clf.predict(training_data.X)
        predict_cv = clf.predict(cv_data.X)
        
        """ Caculate the differences from actual data for training and cv data"""
        diff_training = (1.0/training_data.m) * np.linalg.norm(predict_data - training_data.y)
        diff_cv = (1.0/cv_data.m) * np.linalg.norm(predict_cv - cv_data.y)
        
        """ Write out the values for plotting. Do appropriate work to determine min_val_alpha """
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
        
        

def execute(init_param): 
    """ execute is the function where each run is done. main sets parameters then calls execute"""
    
    training_data, cv_data, test_data = form_data(init_param)
    
    if init_param.output:
        output(training_data, cv_data)
    
    clf, regularization_parameter = learn(training_data, cv_data)
    
    
    """ do an Anderson Darling test on the data to determine if it is a normal fit"""
    A2, sig, crit = anderson(test_data.y, dist = 'norm')
    print("the value for A2 is ", A2)
    
    mn = np.mean(test_data.y)
    sd = np.std(test_data.y)
    print("The mean and standard deviation of the test data are ", mn, sd)
    
    
    predict_data = clf.predict(test_data.X)
    difference = predict_data - test_data.y
    mn = np.mean(difference)
    sd = np.std(difference)
    print("The mean and standard deviation of the difference are ", mn, sd)
    
    print("run finished")
    
class InitialParameters(object):
    """ This class defines an object of parameters used to run the code. It
        is set in main and the parameters are passed to execute """
    
    def __init__(self):
        """ The object is defined with default values that can then be changed in main()"""
        
        #self.max_stocks = 100
        self.max_stocks = 50
        """ cv_factor determines what portion of stocks to put in cross validation set and what portion
            to leave in training set. cv_factor = 2 means every other stock goes into cross validation
            set. cv_factor = 3 means every third stock goes into cross validation set """
        self.cv_factor = 2 
        """ future_day is how many training days in the future we train for. Setting future_day = 25
            means we are measuring how the stock does 25 days out """
        self.future_day = 25
        """ The reference dates are the reference dates we are training on"""
        self.reference_dates = []
        #self.reference_dates.append(dateutil.days_since_1900('1980-01-01'))
        self.reference_dates.append(dateutil.days_since_1900('2000-01-01'))
        """ test_dates are the dates we are using for testing """
        self.test_dates = []
        #self.test_dates.append(dateutil.days_since_1900('1991-01-01'))
        self.test_dates.append(dateutil.days_since_1900('2010-01-01'))
        """train_history_days and train_increment set how many historical days we use to
           train and the increment used. Setting train_history_days = 21 and train_increment = 5
           means we are using the values at days days 5, 10, 15 and 20 days before the reference day
           as input features """
        self.train_days = 21
        self.train_increment = 5
        """ output is just a boolean about calling the output function to write out 
            appropriate X and y matricies. The default is False meaning do not write out
            matricies """
        self.output = False
    
def main(argv):
    
    init_param = InitialParameters()
    #init_param.reference_dates.append(dateutil.days_since_1900('1981-01-01'))
    init_param.reference_dates.append(dateutil.days_since_1900('2001-01-01'))
    execute(init_param)


if __name__ == "__main__":
    main(sys.argv)
