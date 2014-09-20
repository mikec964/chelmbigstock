#!/usr/bin/env python

"""
Hadoop stream API emulator for python mapper/reducer
"""

import os
import sys
import subprocess as sp
import tempfile as tf


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
            self._set_emulator_path(iter_argv.next())
            
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
                    self._reducer = os.path.abspath(arg)
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
                        print >> sys.stderr, "Unknown argument '{}': ignored".format(arg)
        
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


class HSEMapperError(HSEException):
    """
    Raised when mapper reported an error
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
        self._my_python = 'python'
        self._my_path = emu_path
        self._mapper = mapper
        self._reducer = reducer
        self._input_path = input_path
        self._output_path = output_path
        self._user_python = user_python

    def execute(self):
        """
        execute MapReduce job
        """
        with tf.TemporaryFile() as f_sh:
            command = [ self._my_python, os.path.join(self._my_path, 'TextInputFormat.py'), self._input_path ]
            p_input = sp.Popen(command, stdout = sp.PIPE)

            command = [ self._my_python, os.path.join(self._my_path, self._mapper) ]
            p_mapper = sp.Popen(command, stdin = p_input.stdout, stdout = f_sh)
            p_input.stdout.close()   # Allow input process to receive a SIGPIPE,
                                 # if mapper process exits.
            p_mapper.wait()
            p_input.wait()
            if p_input.returncode != 0:
                raise HSEInputFormatterError('Failed to read {}, return code={}: quit'.format(self._input_path, p_input.returncode))
            if p_mapper.returncode != 0:
                raise HSEMapperError('Mapper {} returned error: quit'.format(self._mapper))
            f_sh.seek(0)
            for line in f_sh:
                print line,


# analyze command line arguments
emuopt = analyze_argv(sys.argv)
print 'Mapper={}'.format(emuopt.mapper)
print 'Reducer={}'.format(emuopt.reducer)
print 'Input path={}'.format(emuopt.input_path)
print 'Output path={}'.format(emuopt.output_path)
emulator = HadoopStreamEmulator(
    emuopt.emulator_path,
    emuopt.mapper, emuopt.reducer,
    emuopt.input_path, emuopt.output_path,
    emuopt.python_path
    )
emulator.execute()
