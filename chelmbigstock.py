#!/usr/bin/env python

# A python script to learn about stock picking

import os
from stock import Stock
from learningData import learningData
import numpy as np
from sklearn import datasets, linear_model

def main():
	stock_names = ['ba', 'cat', 'dd', 'ge', 'gs', 'ibm', 'jnj', 'jpm', 'mmm', 'xom']
	#for stock in stocks:
	#   print(stock)
    
        # Andy's comment 2

        # andy's comment

	Stocks = []
	for stock in stock_names:
	    this_stock = Stock(stock, 'data')
	    this_stock.populate()
	    Stocks.append(this_stock)

	trainingData = learningData()
	trainingData.construct(Stocks,['1/1/1980', [50, 100, 150], 50])

	
	clf = linear_model.Ridge (alpha = 0.0, fit_intercept=False)
	clf.fit(trainingData.X, trainingData.y)
	


if __name__ == "__main__":
	main()
