@echo off
setlocal

rem Sample batch file to run the stock MapReduce on the emulator
rem Author: Hideki Ikeda
rem Mar 7, 2015

rem Git directory
set GIT_DIR=%userprofile%\Documents\GitHub

rem Directory of the mapper / reducer
set MAPREDUCE_PATH=%GIT_DIR%\chelmbigstock\mapreduce

rem input data for the mapper
set MR_INPUT_DIR=%MAPREDUCE_PATH%\input

rem result from the reducer
set MR_OUTPUT_DIR=%MAPREDUCE_PATH%\output

rem the emulator directory
set EMULATOR_DIR=%GIT_DIR%\pyhdemu

if exist %MR_OUTPUT_DIR% del /s %MR_OUTPUT_DIR%

python %EMULATOR_DIR%\hdemu.py -input %MR_INPUT_DIR%\stock.csv -output %MR_OUTPUT_DIR% -mapper %MAPREDUCE_PATH%\mapper.py -reducer %MAPREDUCE_PATH%\reducer.py -files %MR_INPUT_DIR%\options.csv
