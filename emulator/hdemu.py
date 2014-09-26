#!/usr/bin/env python

"""
Hadoop stream API emulator for python mapper/reducer

@Author: Hideki Ikeda
Created: September 19, 2014
"""

from __future__ import print_function

import os
import sys
import subprocess as sp
import tempfile as tf


def is_special_reducer(fn_reducer):
    return (fn_reducer == 'aggregate')


def analyze_argv(argv):
    """
    Analyzes command line arguments.
    Arguments:
        List of command line arguments (list of string)
    Return:
        Object with properies; the properties are associated with command line
        arguments.
    """
    
    class CommandLineArguments(object):
        """
        Parses command line arguments and stores them as a property.
        Ignores unknown arguments.
        """
        def __init__(self, argv):
            # default values
            self._python_path = 'python'
            
            # the file path to this emulator
            iter_argv = iter(argv)
            self._set_emulator_path(next(iter_argv))
            
            # state definitions
            sts_init = 0
            sts_mapper = 1
            sts_reducer = 2
            sts_input = 3
            sts_output = 4
            arg_mapper = '-mapper'
            arg_reducer = '-reducer'
            arg_input = '-input'
            arg_output = '-output'
            arg_stss = [ (arg_mapper, sts_mapper),
                         (arg_reducer, sts_reducer),
                         (arg_input, sts_input),
                         (arg_output, sts_output)
                       ]
            def sts_from_arg(arg):
                for i_arg, i_sts in arg_stss:
                    if i_arg == arg:
                        return i_sts
                return sts_init
            
            state = sts_init
            for arg in iter_argv:
                if state == sts_mapper:
                    self._mapper = os.path.abspath(arg)
                    state = sts_init
                elif state == sts_reducer:
                    self._reducer = arg if is_special_reducer(arg) else os.path.abspath(arg)
                    state = sts_init
                elif state == sts_input:
                    self._input_path = os.path.abspath(arg)
                    state = sts_init
                elif state == sts_output:
                    self._output_path = os.path.abspath(arg)
                    state = sts_init
                else:
                    state = sts_from_arg(arg)
                    if state == sts_init:
                        print("Unknown argument '{}': ignored".format(arg), file=sys.stderr)
        
        def _set_emulator_path(self, arg):
            self._emulator_path = os.path.dirname(os.path.abspath(arg))
        
        @property
        def python_path(self):
            return self._python_path
        
        @property
        def emulator_path(self):
            return self._emulator_path
        
        @property
        def mapper(self):
            return self._mapper
        
        @property
        def reducer(self):
            return self._reducer
        
        @property
        def input_path(self):
            return self._input_path
        
        @property
        def output_path(self):
            return self._output_path
    
    return CommandLineArguments(argv)


#
# Hadoop Stream API Emulator
#
# first, exception definitions

class HSEException(Exception):
    """
    Base exception class for HadoopStreamEnulator class
    """
    pass


class HSEInputFormatterError(HSEException):
    """
    Raised when input formatter reported an error
    """
    def __init__(self, msg):
        self.msg = msg


class HSEOutputFormatterError(HSEException):
    """
    Raised when output formatter reported an error
    """
    def __init__(self, msg):
        self.msg = msg


class HSEMapperError(HSEException):
    """
    Raised when mapper reported an error
    """
    def __init__(self, msg):
        self.msg = msg


class HSEReducerError(HSEException):
    """
    Raised when reducer reported an error
    """
    def __init__(self, msg):
        self.msg = msg


class HSEOutputPathError(HSEException):
    """
    Raised when output path already exists
    """
    def __init__(self, msg):
        self.msg = msg


class HadoopStreamEmulator(object):
    """
    Mimics the behavior of the Hadoop stream API.
    """
    def __init__(self, emu_path, mapper, reducer, input_path, output_path, user_python = 'python'):
        """
        Parameters:
            emu_path: the home directory of the emulator
            mapper:   the path to a mapper script in Python
            reducer:  the path to a reducer script in Python
            input_path:  the file name or directory of input data
            output_path: the directory to store result
            user_python: the path to the python interpreter for mapper/reducer
        """
        if os.path.exists(output_path):
            raise HSEOutputPathError("Output path '{}' already exists".format(output_path))

        self._my_python = 'python'
        self._my_path = emu_path
        self._mapper = mapper
        self._reducer = reducer
        self._input_path = input_path
        self._output_path = output_path
        self._user_python = user_python
        self._kv_separator = '\t'

    def shuffle(self, fh):
        """
        Shuffles the result of mapper.
        Argument:
            fh: file handle of the mapper result
        """
        print('**** shuffling ****')
        kv_list = []
        for line in fh:
            a_pair = line.strip().split(self._kv_separator, 1)
            # if a pair doesn't have value, just remove it
            if len(a_pair) != 2:
                continue
            kv_list.append(a_pair)
        kv_list.sort(key = lambda l: l[0])
        return kv_list

    def call_mapper(self, f_out):
        """
        Calls mapper and stores the result in a temp file for shuffling
        """
        print('**** mapping ****')
        command = [ self._my_python, os.path.join(self._my_path, 'TextInputFormat.py'), self._input_path ]
        p_input = sp.Popen(command, stdout = sp.PIPE)

        command = [ self._user_python, self._mapper ]
        p_mapper = sp.Popen(command, stdin = p_input.stdout, stdout = f_out)
        p_input.stdout.close()   # Allow input process to receive a SIGPIPE,
                                 # if mapper process exits.
        p_mapper.wait()
        p_input.wait()
        if p_input.returncode != 0:
            raise HSEInputFormatterError('Failed to read {}, return code={}: quit'.format(self._input_path, p_input.returncode))
        if p_mapper.returncode != 0:
            raise HSEMapperError('Mapper {} returned error: quit'.format(self._mapper))

    def call_reducer(self, f_in, kv_list):
        """
        Calls reducer and stores the result in the 'output' dir
        """
        print('**** reducing ****')
        for kv in kv_list:
            if len(kv) == 1:
                print(kv[0], file=f_in)
            else:
                print('{}\t{}'.format(kv[0], kv[1]), file=f_in)
        f_in.seek(0)

        if self._reducer == 'aggregate':
            command = [ self._my_python, os.path.join(self._my_path, 'aggregate.py') ]
        else:
            command = [ self._user_python, self._reducer ]
        p_reducer = sp.Popen(command, stdin = f_in, stdout = sp.PIPE)

        command = [ self._my_python, os.path.join(self._my_path, 'TextOutputFormat.py'), self._output_path ]
        p_output = sp.Popen(command, stdin = p_reducer.stdout)
        p_reducer.stdout.close()

        p_output.wait()
        p_reducer.wait()

        if p_reducer.returncode != 0:
            raise HSEReducerError('Reducer {} returned error: quit'.format(self._reducer))
        if p_output.returncode != 0:
            raise HSEOutputFormatterError('Failed to write {}, return code={}: quit'.format(self._output_path, p_output.returncode))

    def execute(self):
        """
        execute MapReduce job
        """
        # mapper
        with tf.TemporaryFile(mode='w+') as f_m:
            self.call_mapper(f_m)
            # shuffling
            f_m.seek(0)
            kv_list = self.shuffle(f_m)

        # reducer
        with tf.TemporaryFile(mode='w+') as f_r:
            self.call_reducer(f_r, kv_list)

        print('**** mapreduce job completed ****')


_The_first_lines = [ '#!/usr/bin/env python', '#!/usr/bin/env python3' ]
def is_script_ok(fn_script):
    """
    Make sure a python script exists and it starts with
    #!/usr/bin/env python
    """
    with open(fn_script, 'r') as fh:
        first = fh.readline()
        if first[0] != '#' or not first.strip() in _The_first_lines:
            print("!!!! WARNING !!!! {} dosn't start with one of:".format(fn_script), file=sys.stderr)
            for cmd in _The_first_lines:
                print('\t{}'.format(cmd))


def check_mr(fn_mapper, fn_reducer):
    """
    make sure a mapper and reducer is value
    """
    try:
        is_script_ok(fn_mapper)
    except IOError:
        raise HSEMapperError("Mapper {} doesn't exist: quit".format(fn_mapper))
    try:
        if not is_special_reducer(fn_reducer):
            is_script_ok(fn_reducer)
    except IOError:
        raise HSEReducerError("Reducer {} doesn't exist: quit".format(fn_reducer))


# Hadoop Streaming API emulator for python script
# main

# analyze command line arguments
emuopt = analyze_argv(sys.argv)
print('System     : {}'.format(sys.version))
print('python cmd : {}'.format(emuopt.python_path))
print('Mapper     : {}'.format(emuopt.mapper))
print('Reducer    : {}'.format(emuopt.reducer))
print('Input path : {}'.format(emuopt.input_path))
print('Output path: {}'.format(emuopt.output_path))

try:
    check_mr(emuopt.mapper, emuopt.reducer)
    emulator = HadoopStreamEmulator(
        emuopt.emulator_path,
        emuopt.mapper, emuopt.reducer,
        emuopt.input_path, emuopt.output_path,
        emuopt.python_path
        )
    emulator.execute()
except HSEException as e:
    print('!!!! ERROR !!!! {}'.format(e.msg), file=sys.stderr)
