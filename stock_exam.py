# The python script to learn about stock picking

import os

stock_names = ['ba', 'cat', 'dd', 'ge', 'gs', 'ibm', 'jnj', 'jpm', 'mmm', 'xom']
#for stock in stocks:
#   print(stock)

from stock import Stock

Stocks = []
for stock in stock_names:
    this_stock = Stock(stock, 'data')
    this_stock.populate()
    Stocks.append(this_stock)

from learningData import learningData
trainingData = learningData()
trainingData.construct(Stocks,['1/1/1980', [50, 100, 150], 50])

from LinReg import LinReg
linearRegression = LinReg(trainingData)
linearRegression.calcCost(trainingData)
costArray = linearRegression.gradientDescent(trainingData, 0.1)

f = open('cost.txt', 'w')
for i in range(0, len(costArray)):
    outString = str(i) + ' ' + str(costArray[i])
    f.write(outString)
    f.write('\n')          
f.close()
