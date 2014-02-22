#!/usr/bin/env python

# A python script to learn about stock picking

import os

import numpy as np
from sklearn import linear_model
import math

from stock import Stock
from learningData import learningData

def main():
    stock_names = ['ba', 'cat', 'dd', 'ge', 'gs', 'ibm', 'jnj', 'jpm', 'mmm', 'xom']
    #for stock in stocks:
    #   print(stock)

    Stocks = []
    for stock in stock_names:
        this_stock = Stock(stock, '../data')
        this_stock.populate()
        Stocks.append(this_stock)

    trainingData = learningData()
    trainingData.construct(Stocks,['1/1/1980', [50, 100, 150], 50])
    trainingData.append(Stocks,['1/1/1982', [50, 100, 150], 50])
    
    cv_data = learningData()
    cv_data.construct(Stocks,['1/1/1990', [50, 100, 150], 50])
    cv_data.append(Stocks,['1/1/1992', [50, 100, 150], 50])
    
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
    


if __name__ == "__main__":
    main()
