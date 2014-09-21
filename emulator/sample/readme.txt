***********************************************
* Hadoop Streaming Emulator for Python sample *
***********************************************

**** How to run sample ****

1. Copy the entire 'emulator' directory including the subdirectory
   (this directory) to a work directory

2. In command prompt, go to the sample directory you just copied.

3. Run the command below:

> python ..\hdemu.py -input input -output output -mapper wc_mapper.py -reducer wc_reducer.py

4. When the command finished, make sure the 'output' directory is created.
   Check out the contents.
