# for python 2.7
import sys

def PARALLEL():
    """
    Returns True if we are in the parallel (mapreduce) mode.
    Returns False otherwise.
    """
    return PARALLEL.is_parallel

# initialize the PARALLEL option

# default value
PARALLEL.is_parallel = False

# you can put any initialization code here such as reading the config file
# or checking the environment variables. For demonstration purpose,
# I just check the command line parameter

# set PARALLEL from command line parameters
if '-p' in sys.argv:
    PARALLEL.is_parallel = True
if '-l' in sys.argv:
    PARALLEL.is_parallel = False

