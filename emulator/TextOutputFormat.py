"""
TextOutputFormat module for Hadoop stream API emulator

@Author: Hideki Ikeda
Created: September 19, 2014
"""

from __future__ import print_function

import os
from hseexceptions import HSEOutputPathError

def text_output(kv_separator, f_in, out_dir):
    # copy stdin to result file
    fn_result = os.path.join(out_dir, 'part-00000')
    with open(fn_result, 'w') as fh_result:
        for line in f_in:
            a_pair = line.strip().split(kv_separator, 1)
            if len(a_pair) == 1:
                print('{}\t'.format(a_pair[0]), file=fh_result)
            else:
                print('{}\t{}'.format(a_pair[0], a_pair[1]), file=fh_result)

    # everything went well; make _SUCCESS
    fn_success = os.path.join(out_dir, '_SUCCESS')
    f = open(fn_success, 'w')
    f.close()


def output_formatter(kv_separator, f_in, output_dir):
    """
    Reads key-value pares from a file object and stores them to a directory
    in the Hadoop-like format.
    Parameters:
        f_in:       the input file. the result of reduce
        output_dir: the directory where the result files are stored
    """
    # check if output dir doesn't exist yet
    if os.path.exists(output_dir):
        raise HSEOutputPathError("Output path '{}' already exists".format(output_path))

    # make output dir
    os.mkdir(output_dir)

    text_output(kv_separator, f_in, output_dir)
