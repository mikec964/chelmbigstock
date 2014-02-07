import os

def read_stock(stock, path):
   ''' reads in data about a stock from a csv file of name stock.csv
       found in path path'''

   file = os.path.join(path,stock + '.csv')

   import csv
   with open(file, newline='') as f:
      reader = csv.reader(f)
      headers = f.readline()
      dates = []
      values = []
      for row in reader:
         date = convert_date(row[0])
         # Data in the csv files are in reverse cronological order,
         # insert is used rather than append to put them into cronological
         dates.append(date) 
         values.append(float(row[6]))
      return(dates, values)

def convert_date(date):
   ''' 
       string >- int
       intakes a date month/day/year and returns number of days since 1/1/1900
       convert_date('1/1/1950') -> 18262. Note 1900 was not leap year '''

   daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]  
   dateArray = date.split('/')
   month = int(dateArray[0])
   day = int(dateArray[1])
   year = int(dateArray[2]) - 1900 #looking for number of days since 1900

# Start with days in previous years
   daysPrevYears = year * 365

# Add the appropriate leap years
   leapYears = int(year/4)
   if (year%4 == 0 and month < 3):
      leapYears = leapYears - 1
   daysPrevYears += leapYears

# Now count up the days this year, start with days in previous months
   daysThisYear = 0
   for imonth in range(0,month-1):
      daysThisYear += daysInMonth[imonth]
   
# Add previous days this month
   daysThisYear += day-1


   days = daysPrevYears + daysThisYear
   return(days)
