#!/usr/bin/env python3

# A python script to learn about stock picking
import sys

from operator import itemgetter

import numpy as np
from sklearn import linear_model
from scipy.stats import anderson

import dateutil
from Stock import Stock
from LearningData import LearningData

def construct(max_stocks, future_day):
    """ This function constructs the training, testing and cross validation
        objects for the stock market analysis """
    stocks = Stock.read_stocks('../data/stocks_read.txt', max_stocks)
    stocks_train = []
    stocks_cv = []
    stocks_test = []
    count = 0
    for stock in stocks:
        if count % 2 == 0:
            stocks_train.append(stock)
        else:
            stocks_cv.append(stock)
        count = count + 1
    
    training_data = LearningData()
    cv_data = LearningData()
    test_data = LearningData()
    
    day_history = []
    for i in range(5, 21, 5):
        day_history.append(i)
        
    reference_date = dateutil.days_since_1900('1980-01-01')
    training_data.construct(stocks_train,[reference_date, day_history, future_day])
    cv_data.construct(stocks_cv,[reference_date, day_history, future_day])
    
    reference_date = dateutil.days_since_1900('1981-01-01')
    training_data.append(stocks_train,[reference_date, day_history, future_day])
    cv_data.append(stocks_cv,[reference_date, day_history, future_day])
    
    reference_date = dateutil.days_since_1900('1991-01-01')
    test_data.append(stocks,[reference_date, day_history, future_day])
    
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
        print(" the smallest difference is ", min_diff, " at ", min_alpha)
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
        
        

def main(argv): 
    
    max_stocks = 200
    future_day = 25
    print("the length of argv is ", len(argv))
    for i in range(0,len(argv)):
        print(" this argument is ", i, argv[i])
        if argv[i] == '-max':
            max_stocks = argv[i+1]
        if argv[i] == '-future':
            future_day = argv[i+1]
        if argv[i] == '-start':
            start_dates = argv[i+1]
            print("start_dates = ", start_dates)
            start_list = start_dates.split(',')
            print("start_list = ", start_list)
    print("max_stocks = ", max_stocks)
    
    training_data, cv_data, test_data = construct(max_stocks, future_day)
    
    output(training_data, cv_data)
    
    regularization_parameter = learn(training_data, cv_data)
    
    
    
    
    
    # Construct an LearningData set
  #  reference_date = dateutil.days_since_1900('1984-01-01')
  #  i_day = dateutil.find_ref_date_idx(stocks[0], reference_date)
  #  print (i_day, stocks[0].dates[i_day] )
    """ f = open('value.txt', 'w')
    
    while i_day > 100:
        investing_data.construct(stocks,[reference_date, [50, 100, 150], 50])  
        # Predict growth of stock values based on history
        predict_data = clf.predict(investing_data.X)
        # Predict the stock that will have best growth
        index_max, value = max(enumerate(predict_data), key=itemgetter(1))
        # Upgrade portfolio value based on its actual performance
        portfolio_value = portfolio_value * investing_data.y[index_max]
        average_value = average_value * np.mean(investing_data.y)
        f.write(str(reference_date) + " " + str(portfolio_value) + " " + str(average_value) + "\n")
        #print(portfolio_value)
        i_day = i_day - 50
        reference_date = stocks[0].dates[i_day]
    f.close() """
    
    print("run finished")


if __name__ == "__main__":
    main(sys.argv)
