#!
# This is a sample use of download_data.py.
# From Yahoo finance, it downloads data of the first 10 stocks in the
# ../chelmbigstock/stock_symbols.txt, and stores it in input/stock.csv.

# For details about download_data.py, run download_data.py -h

CHELM_DIR=~/git/chelmbigstock
SYMBOLS=${CHELM_DIR}/chelmbigstock/stock_symbols.txt
INPUT_DIR=${CHELM_DIR}/mapreduce/input
RESULT=${INPUT_DIR}/stock.csv
MAX=200

if [ ! -e $INPUT_DIR ]; then
	mkdir $INPUT_DIR
fi

python ${CHELM_DIR}/mapreduce/download_data.py -s $SYMBOLS -r $RESULT -m $MAX
