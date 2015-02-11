@echo off
setlocal

rem This is a sample use of download_data.py.
rem From Yahoo finance, it downloads data of the first 10 stocks in the
rem ..\chelmbigstock\stock_symbols.txt, and stores it in input\stock.csv.
rem For details about download_data.py, run python download_data.py -h

rem make sure we have the correct version of Python
python --version 2>&1 | find "Python 3"
if errorlevel 1 goto INVALID_PYTHON

if not exist input mkdir input

set SYMBOLS=..\chelmbigstock\stock_symbols.txt
set RESULT=input\stock.csv
set MAX=10

python .\download_data.py -s %SYMBOLS% -r %RESULT% -m %MAX%
goto DONE

:INVALID_PYTHON
echo ERROR! getdata requires Python 3.x

:DONE
