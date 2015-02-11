@echo off
setlocal

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
