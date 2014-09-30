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
from hseexceptions import *
from TextInputFormat import input_formatter
from TextOutputFormat import output_formatter


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
            # the file path to this emulator
            iter_argv = iter(argv)
            self._set_emulator_path(next(iter_argv))
            
            # state definitions
            sts_init = 0
            sts_mapper = 1
            sts_reducer = 2
            sts_input = 3
            sts_output = 4
            sts_interimdir = 5
            arg_mapper = '-mapper'
            arg_reducer = '-reducer'
            arg_input = '-input'
            arg_output = '-output'
            arg_interimdir = '-interim'
            arg_stss = [ (arg_mapper, sts_mapper),
                         (arg_reducer, sts_reducer),
                         (arg_input, sts_input),
                         (arg_output, sts_output),
                         (arg_interimdir, sts_interimdir)
                       ]
            def sts_from_arg(arg):
                for i_arg, i_sts in arg_stss:
                    if i_arg == arg:
                        return i_sts
                return sts_init
            
            # default values
            self._interim_dir = None

            # parse options
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
                elif state == sts_interimdir:
                    self._interim_dir = os.path.abspath(arg)
                    state = sts_init
                else:
                    state = sts_from_arg(arg)
                    if state == sts_init:
                        print("Unknown argument '{}': ignored".format(arg), file=sys.stderr)
        
        def _set_emulator_path(self, arg):
            self._emulator_path = os.path.dirname(os.path.abspath(arg))
        
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

        @property
        def interim_dir(self):
            return self._interim_dir
    
    return CommandLineArguments(argv)


#
# stdio resetter
#
class StdioResetter(object):
    """
    Utility to set / reset stdin and stdout
    """
    def __init__(self, new_stdin = None, new_stdout = None):
        """
        Parameters:
            new_stdin:  File object to set to system stdin. If None, keeps
                        the current stdin
            new_stdout: File object to set to system stdout. If None, keeps
                        the current stdout
        """
        self._org_stdin = sys.stdin
        self._org_stdout = sys.stdout
        if new_stdin != None:
            sys.stdin = new_stdin
        if new_stdout != None:
            sys.stdout = new_stdout

    def restore(self):
        sys.stdin = self._org_stdin
        sys.stdout = self._org_stdout


#
# execute user script
#
def execute_user_scirpt(type_name, file_name, f_in, f_out):
        # compile user script
        try:
            with open(file_name, 'r') as fh:
                user_src = fh.read()
            user_exe = compile(user_src, file_name, 'exec', dont_inherit=True)
        except IOError:
            raise HSEMapperError('{} {} failed to pen: quit'.format(type_name, file_name))
        except SyntaxError as es:
            raise HSEMapperError('{} {} at {} syntax error: quit'.format(type_name, es.filename, es.lineno))
        except TypeError:
            raise HSEMapperError('{} {} type error: quit'.format(type_name, file_name))

        # execute user script
        org_stdio = StdioResetter(f_in, f_out)
        exec(user_exe, globals())
        org_stdio.restore()


#
# Hadoop Stream API Emulator
#
class HadoopStreamEmulator(object):
    """
    Mimics the behavior of the Hadoop stream API.
    """

    # class constants
    _fn_map_input = 'mapper_input.txt'
    _fn_map_output = 'mapper_output.txt'
    _fn_reduce_input = 'reducer_input.txt'
    _fn_reduce_output = 'reducer_output.txt'

    def __init__(self, emu_path,
            mapper, reducer,
            input_path, output_path,
            interim_dir = None):
        """
        Parameters:
            emu_path: the home directory of the emulator
            mapper:   the path to a mapper script in Python
            reducer:  the path to a reducer script in Python
            input_path:  the file name or directory of input data
            output_path: the directory to store result
        """
        if os.path.exists(output_path):
            raise HSEOutputPathError("Output path '{}' already exists".format(output_path))

        if interim_dir != None and os.path.exists(interim_dir):
            raise HSEInterimDirError("Interim directory '{}' already exists".format(interim_dir))

        self._my_python = 'python'
        self._my_path = emu_path
        self._mapper = mapper
        self._reducer = reducer
        self._input_path = input_path
        self._output_path = output_path
        self._interim_dir = interim_dir
        self._kv_separator = '\t'

    def get_file_list(self):
        """
        Return:
            If path is a file, returns a list with the path.
            If path is a directory, returns a list of files in the directory.
            if path is an invalid path, returns None
        """
        if not os.path.exists(self._input_path):
            raise HSEInputPathError("Invalid input path '{}'".format(self._input_path))
        elif os.path.isfile(self._input_path):
            return [self._input_path]
        else:
            lists = []
            for a_file in os.listdir(self._input_path):
                a_path = os.path.join(self._input_path, a_file)
                if os.path.isfile(a_path):
                    lists.append(a_path)
            return lists

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

    def call_mapper(self, f_format, f_out):
        """
        Calls mapper and stores the result in a file for shuffling
        Parameter:
            f_format: file object for input formatter output
            f_out:    file object for mapper output
        """
        print('**** mapping ****')
        input_formatter(self.get_file_list(), f_format)
        f_format.seek(0)

        execute_user_scirpt('Mapper', self._mapper, f_format, f_out)

    def call_reducer(self, kv_list, f_shfl, f_red):
        """
        Calls reducer and stores the result in the 'output' dir
        Parameters:
            kv_list: the reuslt of shuffling. a list of key-value pairs
            f_shfl:  file object to store the kv_list
            f_red:   file object to store the immediate result from reducer
        """
        print('**** reducing ****')
        for kv in kv_list:
            if len(kv) == 1:
                print(kv[0], file=f_shfl)
            else:
                print('{}\t{}'.format(kv[0], kv[1]), file=f_shfl)
        f_shfl.seek(0)

        # use built-in aggregator if user wants
        reducer = os.path.join(self._my_path, 'aggregate.py') if self._reducer == 'aggregate' else self._reducer

        execute_user_scirpt('Reducer', reducer, f_shfl, f_red)

        f_red.seek(0)
        output_formatter(f_red, self._output_path)

    def _execute_temp(self):
        """
        execute MapReduce job with temporary files
        """
        # mapper
        with tf.TemporaryFile(mode='w+') as f_format, tf.TemporaryFile(mode='w+') as f_m:
            self.call_mapper(f_format, f_m)
            # shuffling
            f_m.seek(0)
            kv_list = self.shuffle(f_m)

        # reducer
        with tf.TemporaryFile(mode='w+') as f_s, tf.TemporaryFile(mode='w+') as f_r:
            self.call_reducer(kv_list, f_s, f_r)

    def _execute_interim(self):
        """
        execute MapReduce job; interim results are saved in interim_dir
        """
        fn_map_input = os.path.join(self._interim_dir, HadoopStreamEmulator._fn_map_input)
        fn_map_output = os.path.join(self._interim_dir, HadoopStreamEmulator._fn_map_output)
        fn_reduce_input = os.path.join(self._interim_dir, HadoopStreamEmulator._fn_reduce_input)
        fn_reduce_output = os.path.join(self._interim_dir, HadoopStreamEmulator._fn_reduce_output)
        os.mkdir(self._interim_dir)

        # mapper
        with open(fn_map_input, mode='w+') as f_mi, open(fn_map_output, mode='w+') as f_mo:
            self.call_mapper(f_mi, f_mo)
            # shuffling
            f_mo.seek(0)
            kv_list = self.shuffle(f_mo)

        # reducer
        with open(fn_reduce_input, mode='w+') as f_ri, open(fn_reduce_output, mode='w+') as f_ro:
            self.call_reducer(kv_list, f_ri, f_ro)

    def execute(self):
        """
        execute MapReduce job
        """
        if self._interim_dir == None:
            self._execute_temp()
        else:
            self._execute_interim()

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
print('Mapper     : {}'.format(emuopt.mapper))
print('Reducer    : {}'.format(emuopt.reducer))
print('Input path : {}'.format(emuopt.input_path))
print('Output path: {}'.format(emuopt.output_path))
print('interim dir: {}'.format(emuopt.interim_dir))

try:
    check_mr(emuopt.mapper, emuopt.reducer)
    emulator = HadoopStreamEmulator(
        emuopt.emulator_path,
        emuopt.mapper, emuopt.reducer,
        emuopt.input_path, emuopt.output_path,
        emuopt._interim_dir
        )
    emulator.execute()
except HSEException as e:
    print('!!!! ERROR !!!! {}'.format(e.msg), file=sys.stderr)
