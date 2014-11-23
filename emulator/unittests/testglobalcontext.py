'''
Created on Nov 21, 2014

@author: Hideki Ikeda
'''

import os
import sys
import random
import unittest
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
import hdemu as emu
import hseexceptions as emuex


class DummyException(Exception):
    '''
    Just need an exception to get out of "with EmuGlobalContext()"
    '''
    def __init__(self):
        self.msg = 'DummyException'

    def __str__(self):
        return self.msg


class TestGlobalContext(unittest.TestCase):
    '''
    Unit tests for setting up global context for the emulator
    '''
    _data_path = 'data'
    _data_file = 'glblcntxt.txt'
    _nested_dir = 'nested'
    _nested_file1 = 'file1.txt'
    _nested_file2 = 'file2.txt'
    _mapper = os.path.join(_data_path, 'mockmapper.py')
    _reducer = os.path.join(_data_path, 'mockreducer.py')

    def check_mr(self, context):
        '''
        check if mapper and reducer are correctly copied
        '''
        base_mapper = os.path.basename(self._mapper)
        base_reducer = os.path.basename(self._reducer)
        self.assertTrue(os.path.exists(base_mapper),
                "mapper doesn't exist")
        self.assertTrue(os.path.exists(base_reducer),
                "reducer doesn't exist")
        self.assertEqual(base_mapper, os.path.basename(context.mapper),
                "mapper name doesn't match")
        self.assertNotEqual(base_mapper, context.mapper,
                "mapper path didn't changed")
        self.assertEqual(base_reducer, os.path.basename(context.reducer),
                "reducer name doesn't match")
        self.assertNotEqual(base_reducer, context.reducer,
                "reducer path didn't changed")

    def testEmptyFiles(self):
        '''
        Pass an empty list to EmuGlobalContext
        '''
        org_path = os.getcwd()
        files = []
        with emu.EmuGlobalContext(files, self._mapper, self._reducer) as context:
            cur_path = os.getcwd()
            self.assertEqual(org_path, cur_path,
                    "Empty files test: current directory changed in with:" + cur_path)
        self.assertEqual(org_path, cur_path,
               "Empty files test: current directory changed after with")

    def testAFile(self):
        '''
        Pass a single file to EmuGlobalContext
        '''
        org_path = os.getcwd()
        files = [os.path.join(self._data_path, self._data_file)]

        with emu.EmuGlobalContext(files, self._mapper, self._reducer) as context:
            cur_path = os.getcwd()
            self.assertNotEqual(org_path, cur_path,
                    "A file test: current directory didn't changed in with")
            self.assertTrue(os.path.exists(self._data_file),
                    "A file test: data file doesn't exist")
            self.check_mr(context)
            abs_data_file = os.path.abspath(self._data_file)

        after_path = os.getcwd()
        self.assertEqual(org_path, after_path,
                "A file test: current directory wasn't restored after with")
        self.assertFalse(os.path.exists(abs_data_file),
                "A file test: data file DOES exist after with")

    def testADirectory(self):
        '''
        Pass a single directoty to EmuGlobalContext; The directory contains
        two files
        '''
        org_path = os.getcwd()
        nfile1 = os.path.join(self._nested_dir, self._nested_file1)
        nfile2 = os.path.join(self._nested_dir, self._nested_file2)
        path = [os.path.join(self._data_path, self._nested_dir)]

        with emu.EmuGlobalContext(path, self._mapper, self._reducer) as context:
            cur_path = os.getcwd()
            self.assertNotEqual(org_path, cur_path,
                    "A directory test: current directory didn't change in with")
            self.assertTrue(os.path.exists(self._nested_dir),
                    "A directory test: data directory doesn't exist in with")
            self.assertTrue(os.path.exists(nfile1),
                    "A directory test: file 1 doesn't exist in with")
            self.assertTrue(os.path.exists(nfile2),
                    "A directory test: file 2 doesn't exist in with")
            self.check_mr(context)
            abs_nested_dir = os.path.abspath(self._nested_dir)

        after_path = os.getcwd()
        self.assertEqual(org_path, after_path,
                "A directory test: current directory wasn't restored after with")
        self.assertFalse(os.path.exists(abs_nested_dir),
                "A directory test: data directory DOES exist after with")

    def testComplex(self):
        '''
        Pass a file and a directory to EmuGlobalContext
        '''
        org_path = os.getcwd()
        paths = [os.path.join(self._data_path, self._data_file),
                os.path.join(self._data_path, self._nested_dir)]
        nfile1 = os.path.join(self._nested_dir, self._nested_file1)
        nfile2 = os.path.join(self._nested_dir, self._nested_file2)

        with emu.EmuGlobalContext(paths, self._mapper, self._reducer) as context:
            cur_path = os.getcwd()
            self.assertNotEqual(org_path, cur_path,
                    "Complex test: current directory didn't change in with")
            self.assertTrue(os.path.exists(self._data_file),
                    "A file test: data file doesn't exist")
            self.assertTrue(os.path.exists(self._nested_dir),
                    "Complex test: data directory doesn't exist in with")
            self.assertTrue(os.path.exists(nfile1),
                    "A directory test: file 1 doesn't exist in with")
            self.assertTrue(os.path.exists(nfile2),
                    "A directory test: file 2 doesn't exist in with")
            self.check_mr(context)
            abs_data_file = os.path.abspath(self._data_file)
            abs_nested_dir = os.path.abspath(self._nested_dir)

        after_path = os.getcwd()
        self.assertEqual(org_path, after_path,
                "A directory test: current directory wasn't restored after with")
        self.assertFalse(os.path.exists(abs_data_file),
                "A file test: data file DOES exist after with")
        self.assertFalse(os.path.exists(abs_nested_dir),
                "A directory test: data directory DOES exist after with")

    def testException(self):
        '''
        Throw an exception in "with" statement
        Make sure the current working directory will be restored
        '''
        org_path = os.getcwd()
        files = [os.path.join(self._data_path, self._data_file)]
        raised = False

        try:
            with emu.EmuGlobalContext(files, self._mapper, self._reducer):
                cur_path = os.getcwd()
                self.assertNotEqual(org_path, cur_path,
                        "A file test: current directory didn't changed in with")
                raise DummyException
        except DummyException:
            raised = True

        after_path = os.getcwd()
        self.assertEqual(org_path, after_path,
                "Exception test: current directory wasn't restored after with")
        self.assertTrue(raised, "Exception test: exception was not raised")

    def justReturn(self, org_path):
        '''
        Returns directly from "with" statement
        Sub method for testReturn
        '''
        files = [os.path.join(self._data_path, self._data_file)]

        with emu.EmuGlobalContext(files, self._mapper, self._reducer):
            cur_path = os.getcwd()
            self.assertNotEqual(org_path, cur_path,
                    "A file test: current directory didn't changed in with")
            return

    def testReturn(self):
        org_path = os.getcwd()
        self.justReturn(org_path)
        cur_path = os.getcwd()
        self.assertEqual(org_path, cur_path,
                "Return test: current directory wasn't restored after with")

    def testWrongFile(self):
        org_path = os.getcwd()
        files = [os.path.join(self._data_path, 'does_not_exist')]

        try:
            with emu.EmuGlobalContext(files, self._mapper, self._reducer) as context:
                self.assertTrue(True, "Wrong file test: Shouldn't come in here")
        except IOError as e:
            pass # Expected

        after_path = os.getcwd()
        self.assertEqual(org_path, after_path,
                "Wrong file test: current directory wasn't restored after with")


if __name__ == "__main__":
    unittest.main()
