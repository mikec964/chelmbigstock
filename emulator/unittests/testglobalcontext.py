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

    def setUp(self):
        pass

    def testEmptyFiles(self):
        '''
        Pass an empty list to EmuGlobalContext
        '''
        org_path = os.getcwd()
        files = []
        with emu.EmuGlobalContext(files):
            cur_path = os.getcwd()
            self.assertEqual(org_path, cur_path,
                    "Empty files test: current directory changed in with")
        self.assertEqual(org_path, cur_path,
               "Empty files test: current directory changed after with")

    def testAFile(self):
        '''
        Pass a single file to EmuGlobalContext
        '''
        org_path = os.getcwd()
        data_path, data_file = 'data', 'glblcntxt.txt'
        files = [os.path.join(data_path, data_file)]

        with emu.EmuGlobalContext(files):
            cur_path = os.getcwd()
            self.assertNotEqual(org_path, cur_path,
                    "A file test: current directory didn't changed in with")
            self.assertTure(os.path.exists(data_file),
                    "A file test: data file doesn't exist")
            abs_data_file = os.path.abspath(data_file)

        self.assertEqual(org_path, cur_path,
                "A file test: current directory wasn't restored after with")
        self.assertFalse(os.path.exists(abs_data_file),
                "A file test: data file DOES exist after with")

    def testADirectory(self):
        '''
        Pass a single directoty to EmuGlobalContext; The directory contains
        two files
        '''
        org_path = os.getcwd()
        data_path, nested_dir = 'data', 'nested'
        nfile1 = os.path.join(data_path, 'nested1.txt')
        nfile2 = os.path.join(data_path, 'nested2.txt')
        path = [os.path.join(data_path, nested_dir)]

        with emu.EmuGlobalContext(path):
            cur_path = os.getcwd()
            self.assertNotEqual(org_path, cur_path,
                    "A directory test: current directory didn't change in with")
            self.assertTure(os.path.exists(nested_dir),
                    "A directory test: data directory doesn't exist in with")
            self.assertTrue(os.path.exists(nfile1),
                    "A directory test: file 1 doesn't exist in with")
            self.assertTrue(os.path.exists(nfile2),
                    "A directory test: file 2 doesn't exist in with")
            abs_nested_dir = os.path.abspath(nested_dir)

        self.assertEqual(org_path, cur_path,
                "A directory test: current directory wasn't restored after with")
        self.assertFalse(os.path.exists(abs_nested_dir),
                "A directory test: data directory DOES exist after with")

    def testComplex(self):
        '''
        Pass a file and a direcoty to EmuGlobalContext
        '''
        org_path = os.getcwd()
        data_path, data_file, nested_dir = 'data', 'glblcntxt.txt', 'nested'
        paths = [os.path.join(data_path, data_file), os.path.join(data_path, nested_dir)]
        nfile1 = os.path.join(data_path, 'nested1.txt')
        nfile2 = os.path.join(data_path, 'nested2.txt')

        with emu.EmuGlobalContext(paths):
            cur_path = os.getcwd()
            self.assertNotEqual(org_path, cur_path,
                    "Complex test: current directory didn't change in with")
            self.assertTure(os.path.exists(data_file),
                    "A file test: data file doesn't exist")
            self.assertTrue(os.path.exists(nested_dir),
                    "Complex test: data directory doesn't exist in with")
            self.assertTrue(os.path.exists(nfile1),
                    "A directory test: file 1 doesn't exist in with")
            self.assertTrue(os.path.exists(nfile2),
                    "A directory test: file 2 doesn't exist in with")
            abs_data_file = os.path.abspath(data_file)
            abs_nested_dir = os.path.abspath(nested_dir)

        self.assertEqual(org_path, cur_path,
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
        data_path, data_file = 'data', 'glblcntxt.txt'
        files = [os.path.join(data_path, data_file)]
        raised = False

        try:
            with emu.EmuGlobalContext(files):
                cur_path = os.getcwd()
                self.assertNotEqual(org_path, cur_path,
                        "A file test: current directory didn't changed in with")
                raise DummyException
        except DummyException:
            raised = True

        self.assertEqual(org_path, cur_path,
                "Exception test: current directory wasn't restored after with")
        self.assertTrue(riased, "Exception test: exception was not raised")

    def justReturn(self, org_path):
        '''
        Returns directly from "with" statement
        '''
        data_path, data_file = 'data', 'glblcntxt.txt'
        files = [os.path.join(data_path, data_file)]

        with emu.EmuGlobalContext(files):
            cur_path = os.getcwd()
            self.assertNotEqual(org_path, cur_path,
                    "A file test: current directory didn't changed in with")
            return cur_path

    def testReturn(self):
        org_path = os.getcwd()
        with_path = self.justReturn(org_path)
        self.assertEqual(org_path, with_path,
                "Return test: current directory wasn't restored after with")

if __name__ == "__main__":
    unittest.main()
