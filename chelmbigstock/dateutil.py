

def days_since_1900(date):
    """Convert string date to days since 1/1/1900
    Intakes a date month/day/year and returns number of days since 1/1/1900
    convert_date('1/1/1950') -> 18262. Note 1900 was not leap year
    """

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


def find_ref_date_idx(stock, ref_date):
    """ Find index of ref_date. ref_date might not be a trading day in which case
        we will start with index of first trading day after ref_date
        """
        
    l = 0
    r = len(stock.dates)
    if r == 0:
        return -1        # when no dates, what should we return?
    
    if ref_date < min(stock.dates):
        return -1        # when ref_date is less than all in array return -1

    while l < r - 1:
        m = l + (r - l) // 2
        if stock.dates[m] > ref_date:
            l = m
        elif stock.dates[m] < ref_date:
            r = m
        else:
            return m

    return l

