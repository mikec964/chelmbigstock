#!/usr/bin/env python3

# A python script to learn about stock picking

from operator import itemgetter

import numpy as np
from sklearn import linear_model

import dateutil
from Stock import Stock
from LearningData import LearningData

def main():
    stock_names = ['ba', 'cat', 'dd', 'ge', 'gs', 'ibm', 'jnj', 'jpm', 'mmm', 'xom']
    stock_names = ['mmm']
    stock_names = []
    f = open('stocks_read.txt', 'r')
    count = 0
    max_stocks = 437
    for stock_symbol in f:
        stock_symbol = stock_symbol.strip()
        stock_names.append(stock_symbol)
        count = count + 1
        if count >= max_stocks:
            break
    

    stocks = []
    for stock in stock_names:
        print(stock)
        this_stock = Stock(stock, '../data')
        this_stock.populate()
        stocks.append(this_stock)

    training_data = LearningData()
    reference_date = dateutil.days_since_1900('1980-01-01')
    i_day = dateutil.find_ref_date_idx(stocks[0], reference_date)
   # trainingData.construct(stocks,['1/1/1980', [50, 100, 150], 50])
    training_data.construct(stocks,[reference_date, [50, 100, 150], 50])
    reference_date = dateutil.days_since_1900('1981-01-01')
    training_data.append(stocks,[reference_date, [50, 100, 150], 50])
	
    cv_data = LearningData()
    reference_date = dateutil.days_since_1900('1982-01-01')
    cv_data.construct(stocks,[reference_date, [50, 100, 150], 50])
    reference_date = dateutil.days_since_1900('1983-01-01')
    cv_data.append(stocks,[reference_date, [50, 100, 150], 50])
	
    XX = training_data.X
    clf = linear_model.Ridge(alpha=0.1, fit_intercept=False)
    clf.fit(training_data.X, training_data.y)
	

    # To look for overfitting the code loops through values of alpha plotting distance between
    # the predicted values and actual data and various alphas
    alph = 0.01
    #filename = "output/filename.txt"
    #dir = os.path.dirname(filename)
    f = open('alpha.txt', 'w')
    while alph < 0.2:
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
        # Write out the values
        f.write(str(alph) +  " " + str(diff_data) + " " + str(diff_cv) +  "\n")
        alph = alph * 1.5 # Increment alph
    f.close()
     
     # Do the fit based on best alpha value   
    clf = linear_model.Ridge (alpha=0.05, fit_intercept=False)
    clf.fit(training_data.X, training_data.y)
    
    portfolio_value = 1.0 # Start with a portfolio value of 1.0
    average_value = 1.0
    investing_data = LearningData()
    
    # Construct an LearningData set
    reference_date = dateutil.days_since_1900('1984-01-01')
    i_day = dateutil.find_ref_date_idx(stocks[0], reference_date)
  #  print (i_day, stocks[0].dates[i_day] )
    f = open('value.txt', 'w')
    
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
    f.close()
    
    print("run finished")


if __name__ == "__main__":
    main()
