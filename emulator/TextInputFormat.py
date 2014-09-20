"""
TextInputFormat module for Hadoop stream API emulator
"""

import os
import sys

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
    for fn in f_list:
        with open(fn, 'r') as fh:
            for line in fh:
                print line.strip()

file_list = get_file_list(sys.argv[1])
if file_list == None:
    sys.exit(1)
send_to_mapper(file_list)
