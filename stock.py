class Stock(object):
    ''' The object of a stock '''
    def __init__(self, name, directory):
        ''' The creation of a stock takes in a name assuming it is a
            character string and creates arrays to store dates and
            values'''
        self.name = name
        self.directory = directory
        self.length = 0
        self.dates = []
        self.values = []

    def populate(self):
        ''' This method populates the dates and values of the stock.
            The name of the file is the name of the stock and the directory
            is already known so no arguments are needed'''
        from read_stock import read_stock
        self.dates, self.values = read_stock(self.name, self.directory)


