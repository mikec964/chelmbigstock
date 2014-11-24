%echo off

rem smoke test for Hadoop Streaming emulator for Python
rem Initial: Nov 23, 2014
rem Author: Hideki Ikeda

setlocal

set INPUT=input
set OUTPUT=output
set MAPPER=wc_mapper.py
set REDUCER=wc_reducer.py

rem delete the result of the emulator, if any
if exist %OUTPUT% rmdir /S /Q %OUTPUT%

rem execute a simple mapreduce
python ..\hdemu.py -input %INPUT% -output %OUTPUT% -mapper %MAPPER% -reducer %REDUCER%

if not exist %OUTPUT% (
	set TEST_RESULT=2
) else (
	fc %OUTPUT%\part-00000 expected\part-00000
	set TEST_RESULT=%ERRORLEVEL%
)

echo **********************
echo **** Test Summary ****
echo **********************
if %TEST_RESULT%==0 echo Succeeded
if %TEST_RESULT%==1 echo DIFFERENT from expected
if %TEST_RESULT%==2 echo NO RESULT
if %TEST_RESULT% GTR 2 echo Unknown error code
echo.

rem clean up
echo Cleaning up...
if exist %output% rmdir /S /Q %output%

echo Done.
