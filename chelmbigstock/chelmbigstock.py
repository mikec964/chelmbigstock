#!/usr/bin/env python

# A python script to learn about stock picking
# Anil's test comment

import os

import numpy as np
from sklearn import linear_model
import math
import dateutil
from operator import itemgetter

from stock import Stock
from learningData import learningData
# Andy's comment

def main():
    stock_names = ['ba', 'cat', 'dd', 'ge', 'gs', 'ibm', 'jnj', 'jpm', 'mmm', 'xom']
    

    Stocks = []
    for stock in stock_names:
        this_stock = Stock(stock, '../data')
        this_stock.populate()
        Stocks.append(this_stock)

    trainingData = learningData()
    referenceDate = dateutil.days_since_1900('1/1/1980')
    iDay = dateutil.find_ref_date_idx(Stocks[0], referenceDate)
   # trainingData.construct(Stocks,['1/1/1980', [50, 100, 150], 50])
    trainingData.construct(Stocks,[referenceDate, [50, 100, 150], 50])
    referenceDate = dateutil.days_since_1900('1/1/1981')
    trainingData.append(Stocks,[referenceDate, [50, 100, 150], 50])
	
    cv_data = learningData()
    referenceDate = dateutil.days_since_1900('1/1/1982')
    cv_data.construct(Stocks,[referenceDate, [50, 100, 150], 50])
    referenceDate = dateutil.days_since_1900('1/1/1983')
    cv_data.append(Stocks,[referenceDate, [50, 100, 150], 50])
	
    XX = trainingData.X
    clf = linear_model.Ridge (alpha = 0.1, fit_intercept=False)
    clf.fit(trainingData.X, trainingData.y)
	

    # To look for overfitting the code loops through values of alpha plotting distance between
    # the predicted values and actual data and various alphas
    alph = 0.01
    #filename = "output/filename.txt"
    #dir = os.path.dirname(filename)
    f = open('alpha.txt', 'w')
    while alph < 0.2:
        # First fit the data for each alpha
        clf = linear_model.Ridge (alpha = alph, fit_intercept=False)
        clf.fit(trainingData.X, trainingData.y)
        # Now measure how close model comes for both training data and cross validation data
        # The clf.predict produces a vector with one element for each element in the sample
        predict_data = clf.predict(trainingData.X)
        predict_cv = clf.predict(cv_data.X)
        # The linagl function in np takes a L2 norm of the difference
        diff_data = (1.0/trainingData.m) * np.linalg.norm(predict_data - trainingData.y)
        diff_cv = (1.0/cv_data.m) * np.linalg.norm(predict_cv - cv_data.y)
        # Write out the values
        f.write(str(alph) +  " " + str(diff_data) + " " + str(diff_cv) +  "\n")
        alph = alph * 1.5 # Increment alph
    f.close()
     
     # Do the fit based on best alpha value   
    clf = linear_model.Ridge (alpha = 0.05, fit_intercept=False)
    clf.fit(trainingData.X, trainingData.y)
    
    portfolio_value = 1.0 # Start with a portfolio value of 1.0
    average_value = 1.0
    investingData = learningData()
    
    # Construct an learningData set
    referenceDate = dateutil.days_since_1900('8/2/1984')
    iDay = dateutil.find_ref_date_idx(Stocks[0], referenceDate)
  #  print (iDay, Stocks[0].dates[iDay] )
    f = open('value.txt', 'w')
    
    while iDay > 100:
        investingData.construct(Stocks,[referenceDate, [50, 100, 150], 50])  
        # Predict growth of stock values based on history
        predict_data = clf.predict(investingData.X)
        # Predict the stock that will have best growth
        index_max, value = max(enumerate(predict_data), key=itemgetter(1))
        # Upgrade portfolio value based on its actual performance
        portfolio_value = portfolio_value * investingData.y[index_max]
        average_value = average_value * np.mean(investingData.y)
        f.write(str(referenceDate) + " " + str(portfolio_value) + " " + str(average_value) + "\n")
        #print(portfolio_value)
        iDay = iDay - 50
        referenceDate = Stocks[0].dates[iDay]
    f.close()
    
    print("run finished")


if __name__ == "__main__":
    main()
