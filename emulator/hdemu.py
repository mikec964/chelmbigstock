#!/usr/bin/env python

"""
Hadoop stream API emulator for python mapper/reducer
"""

import os
import sys
import subprocess as sp


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
                    self._mapper = arg
                    state = sts_init
                elif state == sts_reducer:
                    self._reducer = arg
                    state = sts_init
                elif state == sts_input:
                    self._input_path = arg
                    state = sts_init
                elif state == sts_output:
                    self._output_path = arg
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


def run_pipeline(commands):
    """
    Runs commands and connects the stdout of a command with the stdin of the next.
    Arguments:
        commands: list of command. command is the same format as the 'args' argument
        of subprocess.Popen().
    Return:
        List of processes
    """
    previous_p = None
    ps = []
    for command in commands:
        next_stdin = None if previous_p == None else previous_p.stdout
        p = sp.Popen(command, stdin = next_stdin, stdout = sp.PIPE)
        ps.append(p)
        if previous_p:
            previous_p.stdout.close()   # Allow previouse process to receive a SIGPIPE
                                        # if current process exits.
        previous_p = p
    
    return ps


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
        commands = [
                [ self._my_python, os.path.join(self._my_path, 'TextInputFormat.py'), self._input_path ],
                [ self._my_python, os.path.join(self._my_path, 'Shuffle.py') ]
            ]
        ps = run_pipeline(commands)
        output = ps[-1].stdout
        for line in output:
            print line,


# analyze command line arguments
emuopt = analyze_argv(sys.argv)
emulator = HadoopStreamEmulator(
    emuopt.emulator_path,
    emuopt.mapper, emuopt.reducer,
    emuopt.input_path, emuopt.output_path,
    emuopt.python_path
    )
emulator.execute()
