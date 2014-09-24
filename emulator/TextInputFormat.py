"""
TextInputFormat module for Hadoop stream API emulator

@Author: Hideki Ikeda
Created: September 19, 2014
"""

import os
import sys

# exit codes
ERR_NO_ERR = 0
ERR_NO_DIR_GIVEN = 1
ERR_DIR_NOT_EXISTS = 2
ERR_FAILED_TO_READ = 3

def get_file_list(path):
    """
    Arguments:
        path: file name or directory name
    Return:
        If path is a file, returns a list with the path.
        If path is a directory, returns a list of files in the directory.
        if path is an invalid path, returns None
    """
    if not os.path.exists(path):
        return None
    elif os.path.isfile(path):
        return [path]
    else:
        lists = []
        for a_file in os.listdir(path):
            a_path = os.path.join(path, a_file)
            if os.path.isfile(a_path):
                lists.append(a_path)
        return lists


def send_to_mapper(f_list):
    """
    Reads data and send it to mapper through stdout
    """
    for fn in f_list:
        with open(fn, 'r') as fh:
            for line in fh:
                print line.strip()


# get list of files
file_list = get_file_list(sys.argv[1])
if file_list == None:
    sys.exit(ERR_DIR_NOT_EXISTS)

# send data to mapper
try:
    send_to_mapper(file_list)
except:
    ret_val = ERR_FAILED_TO_READ
else:
    ret_val = ERR_NO_ERR

sys.exit(ret_val)
