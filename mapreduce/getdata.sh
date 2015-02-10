#!
# This is a sample use of download_data.py.
# From Yahoo finance, it downloads data of the first 10 stocks in the
# ../chelmbigstock/stock_symbols.txt, and stores it in input/stock.csv.

# For details about download_data.py, run ./download_data.py -h

SYMBOLS=../chelmbigstock/stock_symbols.txt
RESULT=input/stock.csv
MAX=10

python3 ./download_data.py -s $SYMBOLS -r $RESULT -m $MAX
