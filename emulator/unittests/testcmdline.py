'''
Created on Oct 20, 2014

@author: Hideki Ikeda
'''

import os
import sys
import random
import unittest
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
import hdemu as emu
import hseexceptions as emuex


def make_opt_list(list_of_list):
    opt_list = [ x for sublist in list_of_list for x in sublist ]
    opt_list.insert(0, 'hdemu') 
    return opt_list
    

class TestCommandLineOption(unittest.TestCase):
    '''
    Unit tests for analyzing command line options
    '''

    def setUp(self):
        self.opt_input = '-input'
        self.opt_output = '-output'
        self.opt_interim = '-interim'
        self.opt_mapper = '-mapper'
        self.opt_reducer = '-reducer'
        self.opt_cmdenv = '-cmdenv'
        self.data_input = 'data_input'
        self.data_input_path = os.path.abspath(self.data_input)
        self.data_output = 'data_output'
        self.data_output_path = os.path.abspath(self.data_output)
        self.data_interim = 'data_interim'
        self.data_interim_path = os.path.abspath(self.data_interim)
        self.data_mapper = 'data_mapper'
        self.data_mapper_path = os.path.abspath(self.data_mapper)
        self.data_reducer = 'data_reducer'
        self.data_reducer_path = os.path.abspath(self.data_reducer)
        
        self.opt_unknown1 = '-doyouknowme'
        self.opt_unknown2 = 'youdonotknowme'
    
    def testCorrectOptions(self):
        var = 'HSETESTVAR'
        val = 'hsetestval'
        opt_val = var + '=' + val
        list_opts = [ [self.opt_input, self.data_input],
                      [self.opt_output, self.data_output],
                      [self.opt_interim, self.data_interim],
                      [self.opt_mapper, self.data_mapper],
                      [self.opt_reducer, self.data_reducer],
                      [self.opt_cmdenv, opt_val] ]
        
        emu_path = os.path.dirname(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
        pseud_opts = make_opt_list(list_opts)
        args = emu.analyze_argv(pseud_opts)
        self.assertEqual(args.emulator_path, emu_path, 'Emulator directory')
        self.assertEqual(args.input_path, self.data_input_path, 'Input directory')
        self.assertEqual(args.output_path, self.data_output_path, 'Output directory')
        self.assertEqual(args.interim_dir, self.data_interim_path, 'Interim directory')
        self.assertEqual(args.mapper, self.data_mapper_path, 'Mapper')
        self.assertEqual(args.reducer, self.data_reducer_path, 'Reducer')
        ret_var, ret_val = args.cmdenv[0]
        self.assertEqual(ret_var, var, "Environment variable doesn't exist")
        self.assertEqual(ret_val, val, "Environment variable wrong value")
        
        # change the order of options
        random.shuffle(list_opts)
        pseud_opts = make_opt_list(list_opts)
        args = emu.analyze_argv(pseud_opts)
        self.assertEqual(args.input_path, self.data_input_path, 'Input directory')
        self.assertEqual(args.output_path, self.data_output_path, 'Output directory')
        self.assertEqual(args.interim_dir, self.data_interim_path, 'Interim directory')
        self.assertEqual(args.mapper, self.data_mapper_path, 'Mapper')
        self.assertEqual(args.reducer, self.data_reducer_path, 'Reducer')
        ret_var, ret_val = args.cmdenv[0]
        self.assertEqual(ret_var, var, "Environment variable doesn't exist")
        self.assertEqual(ret_val, val, "Environment variable wrong value")

        # change the order of options again
        random.shuffle(list_opts)
        pseud_opts = make_opt_list(list_opts)
        args = emu.analyze_argv(pseud_opts)
        self.assertEqual(args.input_path, self.data_input_path, 'Input directory')
        self.assertEqual(args.output_path, self.data_output_path, 'Output directory')
        self.assertEqual(args.interim_dir, self.data_interim_path, 'Interim directory')
        self.assertEqual(args.mapper, self.data_mapper_path, 'Mapper')
        self.assertEqual(args.reducer, self.data_reducer_path, 'Reducer')
        ret_var, ret_val = args.cmdenv[0]
        self.assertEqual(ret_var, var, "Environment variable doesn't exist")
        self.assertEqual(ret_val, val, "Environment variable wrong value")

    def testCmdenvThree(self):
        '''
        -cmdenv test with three options
        '''
        values = { 'VAR1' : 'val1', 'VAR2' : 'val2', 'VAR3' : 'val3' }
        list_opts = [ [self.opt_cmdenv, var + '=' + values[var]] for var in iter(values) ]
        pseud_opts = make_opt_list(list_opts)
        args = emu.analyze_argv(pseud_opts)

        for var, val in args.cmdenv:
            self.assertTrue(var in values, 'Returned environment variable not match original' + var)
            self.assertEqual(val, values[var], 'Value for {} not match'.format(var))
        self.assertEqual(len(args.cmdenv), len(values), 'the wrong number of items')

    def testCmdenvEmptyVal(self):
        '''
        -cmdenv test with empty value
        '''
        test_var = 'TEST_VAR'
        expected = ''           # empty value
        pseud_opts = make_opt_list( [ [self.opt_cmdenv, test_var + '=' + expected] ] )
        args = emu.analyze_argv(pseud_opts)

        var, val = args.cmdenv[0]
        self.assertTrue(var == test_var, 'Returned environment variable not match original' + var)
        self.assertEqual(val, expected, 'Value for {} not match'.format(var))
        self.assertEqual(len(args.cmdenv), 1, 'the wrong number of items')

    def testCmdenvDup(self):
        '''
        -cmdenv test with duplicate
        '''
        test_var = 'TEST_VAR'
        unexpected = 'unexpected'
        expected = 'expected_value'
        temp_opts = [ [self.opt_cmdenv, test_var + '=' + unexpected], [self.opt_cmdenv, test_var + '=' + expected] ]
        pseud_opts = make_opt_list(temp_opts)
        args = emu.analyze_argv(pseud_opts)

        var, val = args.cmdenv[0]
        self.assertTrue(var == test_var, 'Returned environment variable not match original' + var)
        self.assertEqual(val, expected, 'Value for {} not match'.format(var))
        self.assertEqual(len(args.cmdenv), 1, 'the wrong number of items')

    def testCmdenvNoValue(self):
        '''
        -cmdenv test with duplicate
        '''
        test_var = 'TEST_VAR'
        expected = 'expected_value'
        # 'TEST_VAR=expected_value' and 'TEST_VAR'
        # arg w/o the value part must be ignored
        temp_opts = [ [self.opt_cmdenv, test_var + '=' + expected], [self.opt_cmdenv, test_var] ]
        pseud_opts = make_opt_list( temp_opts )
        args = emu.analyze_argv(pseud_opts)

        var, val = args.cmdenv[0]
        self.assertTrue(var == test_var, 'Returned environment variable not match original' + var)
        self.assertEqual(val, expected, 'Value for {} not match'.format(var))
        self.assertEqual(len(args.cmdenv), 1, 'the wrong number of items')

    def testUnknownOptions(self):
        '''
        Unknown options should be gracefully ignored with error message
        to stderr
        TODO : add error message test 
        '''
        list_opts = [ [self.opt_unknown1],
                      [self.opt_input, self.data_input],
                      [self.opt_output, self.data_output],
                      [self.opt_mapper, self.data_mapper],
                      [self.opt_reducer, self.data_reducer],
                      [self.opt_unknown2] ]
        
        emu_path = os.path.dirname(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
        pseud_opts = make_opt_list(list_opts)
        args = emu.analyze_argv(pseud_opts)
        self.assertEqual(args.emulator_path, emu_path, 'Emulator directory')
        self.assertEqual(args.input_path, self.data_input_path, 'Input directory')
        self.assertEqual(args.output_path, self.data_output_path, 'Output directory')
        self.assertEqual(args.mapper, self.data_mapper_path, 'Mapper')
        self.assertEqual(args.reducer, self.data_reducer_path, 'Reducer')
        
        # change the order of options
        random.shuffle(list_opts)
        pseud_opts = make_opt_list(list_opts)
        args = emu.analyze_argv(pseud_opts)
        self.assertEqual(args.input_path, self.data_input_path, 'Input directory')
        self.assertEqual(args.output_path, self.data_output_path, 'Output directory')
        self.assertEqual(args.mapper, self.data_mapper_path, 'Mapper')
        self.assertEqual(args.reducer, self.data_reducer_path, 'Reducer')

        # change the order of options again
        random.shuffle(list_opts)
        pseud_opts = make_opt_list(list_opts)
        args = emu.analyze_argv(pseud_opts)
        self.assertEqual(args.input_path, self.data_input_path, 'Input directory')
        self.assertEqual(args.output_path, self.data_output_path, 'Output directory')
        self.assertEqual(args.mapper, self.data_mapper_path, 'Mapper')
        self.assertEqual(args.reducer, self.data_reducer_path, 'Reducer')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
