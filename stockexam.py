#!/usr/bin/env python

# A python script to learn about stock picking

import os
from stock import Stock
from learningData import learningData
from LinReg import LinReg

def main():
	stock_names = ['ba', 'cat', 'dd', 'ge', 'gs', 'ibm', 'jnj', 'jpm', 'mmm', 'xom']
	#for stock in stocks:
	#   print(stock)
    
        # Andy's comment 2

	Stocks = []
	for stock in stock_names:
	    this_stock = Stock(stock, 'data')
	    this_stock.populate()
	    Stocks.append(this_stock)

	trainingData = learningData()
	trainingData.construct(Stocks,['1/1/1980', [50, 100, 150], 50])

	linearRegression = LinReg(trainingData)
	linearRegression.calcCost(trainingData)
	costArray = linearRegression.gradientDescent(trainingData, 0.1)

	f = open('cost.txt', 'w')
	for i in range(0, len(costArray)):
	    outString = str(i) + ' ' + str(costArray[i])
	    f.write(outString)
	    f.write('\n')          
	f.close()


if __name__ == "__main__":
	main()
