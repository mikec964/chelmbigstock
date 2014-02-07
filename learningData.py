class learningData(object):
    ''' The object of data. This object will be composed
        from an array of stocks and dates. It will consist
        of both input data (xs) and output data (ys). '''
    def __init__(self):
        ''' The data is originally two empty array. The first array will be
            two dimensional input array called x that is m x n. The second
            array called y is the output array that is m x 1. The number of
            stocks is denoted by m and the number of dates used for learning
            is denoted by n. All notation is to be consistant with the
            Coursera Machine Learning course as much as possible.'''
        self.X = []
        self.y = []
        self.m = 0
        self.n = 0

    def construct(self, stocks, dates):
        ''' This method constructs the data arrays. The inputs are an array
            of m stocks and an array of dates. The first element of dates
            is a character string to tell the referenced date such as
            '1/1/1980'. The second element is an array of n-1 integers
            telling the trading days to use to populate the input array.
            The final value is the integer value of the future date.
            An input value of ['1/1/1980',[50, 100, 150], 50] means
            we are using '1/1/1980' as our reference date along with the
            dates 50 trading days, 100 trading days and 150 trading days
            in the past for a total of 4 input values i.e. n = 4. From
            these values we are looking to anticipate the stock value
            50 days in the future. 

            The value of m for the data is expected to be m but not all stocks
            go back as far in time. If 1/1/1980 is the reference date and
            gs only went public in 1999 this stock will be left out of the
            Data object.

            '''
        self.n = len(dates[1]) + 1
        self.m = 0
        from stock import Stock
        from read_stock import convert_date
        referenceDate = convert_date(dates[0])
        num_stocks = len(stocks)
        print (referenceDate)
        self.m = 0
        for i in range(0, num_stocks):
            elements = len(stocks[i].dates) # This is the number of entries in stocks
            firstDayAvailable = stocks[i].dates[elements-1]
            firstDayNeeded = referenceDate - max(dates[1]) # How far back I need to go
            if (firstDayNeeded > firstDayAvailable): 
                self.m += 1
                # Find index of referenceDate. refererenceDate might not be a trading
                # day in which case we will start with index of first trading day
                # after referenceDay
                iDay = 0
                while (stocks[i].dates[iDay] >= referenceDate):
                    iDay += 1
                if (stocks[i].dates[iDay] < referenceDate):
                    iDay -= 1
                stockDays = []
                stockDays.append(iDay)
                # Construct an array of indicies of values to constuct from
                for iMark in range(0, len(dates[1])):
                    stockDays.append(iDay + dates[1][iMark])
                # Now go through array of indicies and get the trading values of those days
                tempValues = []
                referenceValue = stocks[i].values[iDay] # All values for this stock are divided by this
                for iMark in range(0, len(stockDays)):
                    # divide stock value by value on reference date 
                    adjustedValue = stocks[i].values[stockDays[iMark]]/referenceValue
                    tempValues.append(adjustedValue)
                self.X.append(tempValues)
                # Now get the future value and append it to self.y
                futureDay = iDay - dates[2]
                adjustedValue = stocks[i].values[futureDay]/referenceValue
                self.y.append(adjustedValue)
                                   
            
        
        
        
    
