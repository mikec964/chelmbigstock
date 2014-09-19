#!/usr/bin/env python3

# A python script to learn about stock picking
import sys

from operator import itemgetter

import numpy as np
from sklearn import linear_model

import dateutil
from Stock import Stock
from LearningData import LearningData

def construct(max_stocks, future_day):
    """ This function constructs the training, testing and cross validation
        objects for the stock market analysis """
    stocks = Stock.read_stocks('../data/stocks_read.txt', max_stocks)
    stocks_train = []
    stocks_cv = []
    count = 0
    for stock in stocks:
        if count % 2 == 0:
            stocks_train.append(stock)
        else:
            stocks_cv.append(stock)
        count = count + 1
    
    training_data = LearningData()
    cv_data = LearningData()
    
    day_history = []
    for i in range(5, 21, 5):
        day_history.append(i)
        
    reference_date = dateutil.days_since_1900('1980-01-01')
    training_data.construct(stocks_train,[reference_date, day_history, future_day])
    cv_data.construct(stocks_cv,[reference_date, day_history, future_day])
    
    reference_date = dateutil.days_since_1900('1981-01-01')
    training_data.append(stocks_train,[reference_date, day_history, future_day])
    cv_data.append(stocks_cv,[reference_date, day_history, future_day])
    
    return training_data, cv_data

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

def main(argv):
    
    max_stocks = 30
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
    
    training_data, cv_data = construct(max_stocks, future_day)
    
    output(training_data, cv_data)
    
    """reference_date = dateutil.days_since_1900('1981-01-01')
    training_data.append(stocks_train,[reference_date, [50, 100, 150], 50])
    cv_data.append(stocks_cv,[reference_date, [50, 100, 150], 50])"""
    """reference_date = dateutil.days_since_1900('1980-01-01')
    i_day = dateutil.find_ref_date_idx(stocks[0], reference_date)
   # trainingData.construct(stocks,['1/1/1980', [50, 100, 150], 50])
    training_data.construct(stocks,[reference_date, [50, 100, 150], 50])
    reference_date = dateutil.days_since_1900('1981-01-01')
    training_data.append(stocks,[reference_date, [50, 100, 150], 50])
	
    cv_data = LearningData()
    reference_date = dateutil.days_since_1900('1982-01-01')
    cv_data.construct(stocks,[reference_date, [50, 100, 150], 50])
    reference_date = dateutil.days_since_1900('1983-01-01')
    cv_data.append(stocks,[reference_date, [50, 100, 150], 50])"""
	
    XX = training_data.X
    clf = linear_model.Ridge(alpha=0.1, fit_intercept=False)
    clf.fit(training_data.X, training_data.y)
	

    # To look for overfitting the code loops through values of alpha plotting distance between
    # the predicted values and actual data and various alphas
    print(training_data.m, cv_data.m)
    aa = a = np.array((0, 0, 0, 0))
    bb = a = np.array((1, 1, 1, 1))
    print(np.linalg.norm(bb - aa))
    alph = 0.02
    f = open('alpha.txt', 'w')
    while alph < 0.2:  #0.2
        # First fit the data for each alpha
        clf = linear_model.Ridge (alpha=alph, fit_intercept=False)
        clf.fit(training_data.X, training_data.y)
        # Now measure how close model comes for both training data and cross validation data
        # The clf.predict produces a vector with one element for each element in the sample
        predict_data = clf.predict(training_data.X)
        predict_cv = clf.predict(cv_data.X)
        # The linagl function in np takes a L2 norm of the difference
        diff_data = (1.0/training_data.m) * np.linalg.norm(predict_data - training_data.y)
        diff_cv = (1.0/cv_data.m) * np.linalg.norm(predict_cv - cv_data.y)
        print("lengths are ", len(predict_data), len(training_data.y), len(predict_cv), len(cv_data.y))
        # Write out the values
        f.write(str(alph) +  " " + str(diff_data) + " " + str(diff_cv) +  "\n")
        """print(diff_data, diff_cv)
        print(predict_data - training_data.y)
        print(predict_cv - cv_data.y)"""
        alph = alph * 1.5 # Increment alph
    f.close()
     
     # Do the fit based on best alpha value   
    clf = linear_model.Ridge (alpha=0.05, fit_intercept=False)
    clf.fit(training_data.X, training_data.y)
    
    portfolio_value = 1.0 # Start with a portfolio value of 1.0
    average_value = 1.0
    investing_data = LearningData()
    
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
