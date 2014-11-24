%echo off

rem smoke test for Hadoop Streaming emulator for Python
rem Initial: Nov 23, 2014
rem Author: Hideki Ikeda

setlocal

set INPUT=input
set OUTPUT=output

rem delete the result of the emulator, if any
if exist %OUTPUT% rmdir /S /Q %OUTPUT%

rem execute a simple mapreduce
echo Simple test...
python ..\hdemu.py -input %INPUT% -output %OUTPUT% -mapper wc_mapper.py -reducer wc_reducer.py

if not exist %OUTPUT% (
	set SIMPLE_RESULT=2
) else (
	fc %OUTPUT%\part-00000 expected\part-00000
	set SIMPLE_RESULT=%ERRORLEVEL%
)

rem clean up
echo Cleaning up...
if exist %output% rmdir /S /Q %output%

rem execute a -files mapreduce
echo Files test...
python ..\hdemu.py -input %INPUT% -output %OUTPUT% -mapper f_mapper.py -reducer f_reducer.py -files f_file.txt

if not exist %OUTPUT% (
	set FILES_RESULT=2
) else (
	fc %OUTPUT%\part-00000 expected\f-00000
	set FILES_RESULT=%ERRORLEVEL%
)

rem clean up
echo Cleaning up...
if exist %output% rmdir /S /Q %output%

echo **********************
echo **** Test Summary ****
echo **********************
if %SIMPLE_RESULT%==0 echo Simple test Succeeded
if %SIMPLE_RESULT%==1 echo Simple test DIFFERENT from expected
if %SIMPLE_RESULT%==2 echo Simple test NO RESULT
if %SIMPLE_RESULT% GTR 2 echo Simple test Unknown error code

if %FILES_RESULT%==0 echo Files test Succeeded
if %FILES_RESULT%==1 echo Files test DIFFERENT from expected
if %FILES_RESULT%==2 echo Files test NO RESULT
if %SIMPLE_RESULT% GTR 2 echo Unknown error code

echo.

echo Done.
