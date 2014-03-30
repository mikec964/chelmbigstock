import os
import csv

import dateutil


class Stock(object):
    """A stock has a symbol and a list of date/value pairs"""
    
    def __init__(self, name, directory):
        """ The creation of a stock takes in a name assuming it is a
            character string and creates arrays to store dates and
            values
            """
            
        self.name = name
        self.directory = directory
        self.length = 0
        self.dates = []
        self.values = []

    def populate(self):
        """ This method populates the dates and values of the stock.

        The name of the file is the name of the stock and the directory
        is already known so no arguments are needed
        """

        file = os.path.join(self.directory, self.name + '.csv')
        with open(file, 'U') as f:
            reader = csv.reader(f)
            headers = f.readline()
            dates = []
            values = []
            for row in reader:
                try:
                    date = dateutil.days_since_1900(row[0])
                    # Data in the csv files are in reverse cronological order,
                    # insert is used rather than append to put them into cronological
                    dates.append(date) 
                    values.append(float(row[6]))
                except:
                    continue
             #       print("empty row")
        self.dates, self.values = dates, values
