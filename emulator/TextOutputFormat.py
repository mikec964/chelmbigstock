"""
TextOutputFormat module for Hadoop stream API emulator

@Author: Hideki Ikeda
Created: September 19, 2014
"""

import os
import sys

# exit codes
ERR_NO_ERR = 0
ERR_NO_DIR_GIVEN = 1
ERR_DIR_ALREADY_EXISTS = 2
ERR_FAILED_TO_WRITE = 3

def text_output(out_dir):
    # copy stdin to result file
    fn_result = os.path.join(out_dir, 'part-00000')
    with open(fn_result, 'w') as fh_result:
        for line in sys.stdin:
            print >> fh_result, line,

    # everything went well; make _SUCCESS
    fn_success = os.path.join(out_dir, '_SUCCESS')
    f = open(fn_success, 'w')
    f.close()

# check if output dir is given
output_dir = sys.argv[1]
if output_dir == None:
    sys.exit(ERR_NO_DIR_GIVEN)

# check if output dir doesn't exist yet
if os.path.exists(output_dir):
    sys.exit(ERR_DIR_ALREADY_EXISTS)

# make output dir
os.mkdir(output_dir)

# output the text to files
try:
    text_output(output_dir)
except:
    ret_val = ERR_FAILED_TO_WRITE
else:
    ret_val = ERR_NO_ERR

sys.exit(ret_val)
