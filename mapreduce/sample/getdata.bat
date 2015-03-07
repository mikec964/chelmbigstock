@echo off
setlocal

rem This is a sample use of download_data.py.
rem From Yahoo finance, it downloads data of the first 200 stocks in the
rem ..\chelmbigstock\stock_symbols.txt, and stores it in input\stock.csv.
rem For details about download_data.py, run python download_data.py -h

if not exist input mkdir input

set CHELM_DIR=%userprofile%\Documents\GitHub\chelmbigstock
set SYMBOLS=%CHELM_DIR%\chelmbigstock\stock_symbols.txt
set RESULT=%CHELM_DIR%\mapreduce\input\stock.csv
set MAX=200

python %CHELM_DIR%\mapreduce\download_data.py -s %SYMBOLS% -r %RESULT% -m %MAX%
goto DONE

:DONE
