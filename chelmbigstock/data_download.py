'''
Created on Mar 15, 2014

@author: Andy Webber
'''
from urllib import request

# Retrieve the webpage as a string
response = request.urlopen("http://ichart.finance.yahoo.com/table.csv?s=AAPL&amp;d=1&amp;e=1&amp;f=2014&amp;g=d&amp;a=8&amp;b=7&amp;c=1984&amp;ignore=.csv")
csv = response.read()

# Save the string to a file
csvstr = str(csv).strip("b'")

lines = csvstr.split("\\n")
f = open("historical.csv", "w")
for line in lines:
   f.write(line + "\n")
f.close()