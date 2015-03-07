@echo off
setlocal

rem This is a sample use of mkmropt.py
rem Input:
rem       input\mkmropt.ini
rem Output:
rem       input\result.csv

rem For details about mkmropt.py, run python mkmropt.py -h

set CHELM_DIR=%userprofile%\Documents\GitHub\chelmbigstock
set MAPRED_DIR=%CHELM_DIR%\mapreduce
set SAMPLE_DIR=%MAPRED_DIR%\sample

python %MAPRED_DIR%\mkmropt.py %SAMPLE_DIR%\mkmroptwin.ini
