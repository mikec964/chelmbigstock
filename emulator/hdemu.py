#!/usr/bin/env python

"""
Hadoop stream API emulator for python mapper/reducer

@Author: Hideki Ikeda
Created: September 19, 2014
"""

from __future__ import print_function

import os
import sys
import tempfile as tf
import shutil as su
import hseexceptions as excp
from TextInputFormat import input_formatter
from TextOutputFormat import output_formatter


def is_builtin_reducer(fn_reducer):
    """
    Returns True if fn_reducer specifies the built-in reducer.
    """
    return (fn_reducer == 'aggregate')


def analyze_argv(argv):
    """
    Analyzes command line arguments.
    Arguments:
        List of command line arguments (list of string)
    Return:
        Object with properties; the properties are associated with command line
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
            def sts_init(arg):
                state = opt_stss[arg] if arg in opt_stss else sts_init
                if state == sts_init:
                    print("Unknown argument '{}': ignored".format(arg), file=sys.stderr)
                return state
                
            def sts_mapper(arg):
                self._mapper = os.path.abspath(arg)
                return sts_init
            sts_mapper.opt = '-mapper' 
            
            def sts_reducer(arg):
                self._reducer = arg if is_builtin_reducer(arg) else os.path.abspath(arg)
                return sts_init
            sts_reducer.opt = '-reducer'
            
            def sts_input(arg):
                self._input_path = os.path.abspath(arg)
                return sts_init
            sts_input.opt = '-input'
            
            def sts_output(arg):
                self._output_path = os.path.abspath(arg)
                return sts_init
            sts_output.opt = '-output'
            
            def sts_interimdir(arg):
                self._interim_dir = os.path.abspath(arg)
                return sts_init
            sts_interimdir.opt = '-interim'
            # default values
            self._interim_dir = None
            
            def sts_cmdenv(arg):
                var_val = arg.split('=', 1)
                if len(var_val) == 2:
                    self._cmdenv_dict[var_val[0]] = var_val[1]
                return sts_init
            sts_cmdenv.opt = '-cmdenv'
            self._cmdenv_dict = {}
            self._cmdenv = None     # default value

            def sts_files(arg):
                file_list = arg.split(',')
                if len(file_list) > 0:
                    self._files.extend(file_list)
                return sts_init
            sts_files.opt = '-files'
            self._files = []        # default value

            opt_stss = { sts_mapper.opt : sts_mapper,
                         sts_reducer.opt : sts_reducer,
                         sts_input.opt : sts_input,
                         sts_output.opt : sts_output,
                         sts_interimdir.opt : sts_interimdir,
                         sts_cmdenv.opt : sts_cmdenv,
                         sts_files.opt : sts_files
                       }

            # parse options
            state = sts_init
            for arg in iter_argv:
                state = state(arg)

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

        @property
        def cmdenv(self):
            if self._cmdenv is None:
                self._cmdenv = [ (var, self._cmdenv_dict[var]) for var in iter(self._cmdenv_dict) ]
            return self._cmdenv

        @property
        def files(self):
            return self._files
    
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
# Global context setter of the emulator
#
class EmuGlobalContext(object):
    """
    Set up the runtime environment for mapper/reducer
    """
    def __init__(self, files = None, mapper = None, reducer = None):
        self._files = files
        self._mapper = mapper
        self._reducer = reducer

    def __enter__(self):
        if self._files is None or len(self._files) == 0:
            self._org_path = None
        else:
            self._org_path = os.getcwd()
            self._tmp_path = tf.mkdtemp()
            try:
                for p in self._files:
                    if os.path.isdir(p):
                        base = os.path.basename(p)
                        su.copytree(p, os.path.join(self._tmp_path, base))
                    else:
                        su.copy(p, self._tmp_path)

                if self._mapper is not None:
                    su.copy(self._mapper, self._tmp_path)
                    self._mapper = os.path.abspath(
                            os.path.join(self._tmp_path, os.path.basename(self._mapper)))

                if self._reducer is not None:
                    su.copy(self._reducer, self._tmp_path)
                    self._reducer = os.path.abspath(
                            os.path.join(self._tmp_path, os.path.basename(self._reducer)))

                os.chdir(self._tmp_path)
            except:
                self._org_path = None
                su.rmtree(self._tmp_path)
                raise

        return self

    def __exit__(self, *args):
        if self._org_path is not None:
            os.chdir(self._org_path)
            su.rmtree(self._tmp_path)

        return False

    @property
    def mapper(self):
        return self._mapper

    @property
    def reducer(self):
        return self._reducer


#
# execute user script
#
def execute_user_scirpt(type_name, file_name, f_in, f_out):
    """
    Runs a python script with given stdio.
    Parameters:
        type_name: String used for a exception message. Typically 'Mapper' or
                   'Reducer'
        file_name: The file name of the Python script to run
        f_in:    : File object for data input. Used as stdin during execution.
        f_out:   : File object for data output. Used as stdout.
    """
    # compile user script
    try:
        with open(file_name, 'r') as fh:
            user_src = fh.read()
        user_exe = compile(user_src, file_name, 'exec', dont_inherit=True)
    except IOError:
        raise excp.HSEMapperError('{} {} failed to pen: quit'.format(type_name, file_name))
    except SyntaxError as es:
        raise excp.HSEMapperError('{} {} at {} syntax error: quit'.format(type_name, es.filename, es.lineno))
    except TypeError:
        raise excp.HSEMapperError('{} {} type error: quit'.format(type_name, file_name))

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
            interim_dir = None,
            cmdenv = None,
            files = None):
        """
        Parameters:
            emu_path: the home directory of the emulator
            mapper:   the path to a mapper script in Python
            reducer:  the path to a reducer script in Python
            input_path:  the file name or directory of input data
            output_path: the directory to store result
            interim_dir: the directory to store interim results
                         mapper input/ouput, reducer input/output
            cmdenv:    : the list of environment variable to pass mapper/reducer
        """
        if os.path.exists(output_path):
            raise excp.HSECommandLineError("Output path '{}' already exists".format(output_path))

        if interim_dir is not None and os.path.exists(interim_dir):
            raise excp.HSECommandLineError("Interim directory '{}' already exists".format(interim_dir))

        if cmdenv is not None:
            for var, val in cmdenv:
                os.environ[var] = val

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
            raise excp.HSECommandLineError("Invalid input path '{}'".format(self._input_path))
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
                print('{}\t'.format(kv[0]), file=f_shfl)
            else:
                print('{}\t{}'.format(kv[0], kv[1]), file=f_shfl)
        f_shfl.seek(0)

        # use built-in aggregator if user wants
        reducer = os.path.join(self._my_path, 'aggregate.py') if self._reducer == 'aggregate' else self._reducer

        execute_user_scirpt('Reducer', reducer, f_shfl, f_red)

        f_red.seek(0)
        output_formatter(self._kv_separator, f_red, self._output_path)

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
        raise excp.HSEMapperError("Mapper {} doesn't exist: quit".format(fn_mapper))
    try:
        if not is_builtin_reducer(fn_reducer):
            is_script_ok(fn_reducer)
    except IOError:
        raise excp.HSEReducerError("Reducer {} doesn't exist: quit".format(fn_reducer))


# Hadoop Streaming API emulator for python script
if __name__ == '__main__':
    # analyze command line arguments
    emuopt = analyze_argv(sys.argv)
    print('System     : {}'.format(sys.version))
    print('Mapper     : {}'.format(emuopt.mapper))
    print('Reducer    : {}'.format(emuopt.reducer))
    print('Input path : {}'.format(emuopt.input_path))
    print('Output path: {}'.format(emuopt.output_path))
    print('interim dir: {}'.format(emuopt.interim_dir))
    for var, val in emuopt.cmdenv:
        print('cmdenv     : {}={}'.format(var, val))
    for f in emuopt.files:
        print('files      : {}'.format(f))
    
    try:
        check_mr(emuopt.mapper, emuopt.reducer)
        emulator = HadoopStreamEmulator(
            emuopt.emulator_path,
            emuopt.mapper, emuopt.reducer,
            emuopt.input_path, emuopt.output_path,
            emuopt.interim_dir,
            emuopt.cmdenv
            )
        emulator.execute()
    except excp.HSEException as e:
        print('!!!! ERROR !!!! {}'.format(e.msg), file=sys.stderr)
