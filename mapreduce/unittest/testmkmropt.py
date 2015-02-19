#!/usr/bin/env python

'''
Created on Oct 24, 2014

@author: Hideki Ikeda
'''

import os
import sys
import tempfile
import filecmp
import unittest
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
import mkmropt as target


class TestPreprocess(unittest.TestCase):
    '''
    Unit tests
    '''

    @classmethod
    def setUpClass(self):
        self.data_dir = 'data'
        self.test_symbol_file = os.path.join(self.data_dir, 'test_symbols.txt')
        self.expected_all = os.path.join(self.data_dir, 'expected_all.csv')
        self.result_all = os.path.join(self.data_dir, 'result_all.csv')
        self.expected_two = os.path.join(self.data_dir, 'expected_two.csv')
        self.result_two = os.path.join(self.data_dir, 'result_two.csv')
        self.expected_datasets_all = os.path.join(self.data_dir,
                'expected_datasets_all.txt')
        self.expected_datasets_all3 = os.path.join(self.data_dir,
                'expected_datasets_all3.txt')

        self.test_bad_symbol_file = os.path.join(self.data_dir, 'test_symbols_with_bad.txt')
        self.expected_bad = os.path.join(self.data_dir, 'expected_two.csv') # reuse the result
        self.result_bad = os.path.join(self.data_dir, 'result_bad.csv')

    @classmethod
    def tearDownClass(self):
        if os.path.exists(self.result_all):
            os.remove(self.result_all)
        if os.path.exists(self.result_two):
            os.remove(self.result_two)
        if os.path.exists(self.result_bad):
            os.remove(self.result_bad)

    def testTypeGenerator(self):
        # default
        gen = target.data_type_generator()
        self.assertEqual(gen.next(), 'TR')
        self.assertEqual(gen.next(), 'CV')
        self.assertEqual(gen.next(), 'TR')
        self.assertEqual(gen.next(), 'CV')

        # factor = 3
        gen = target.data_type_generator(3)
        self.assertEqual(gen.next(), 'TR')
        self.assertEqual(gen.next(), 'TR')
        self.assertEqual(gen.next(), 'CV')
        self.assertEqual(gen.next(), 'TR')
        self.assertEqual(gen.next(), 'TR')
        self.assertEqual(gen.next(), 'CV')
        self.assertEqual(gen.next(), 'TR')

    def testReadSymbols(self):
        with open(self.test_symbol_file, 'r') as f_test:
            expected = [ line.strip() for line in f_test ]
        result = target.read_symbols(self.test_symbol_file)
        self.assertEqual(expected, result, 'Target returned: {}'.format(result))

    def testReadSymbols5(self):
        max_stocks = 5
        with open(self.test_symbol_file, 'r') as f_test:
            expected = [ line.strip() for line in f_test ]
        expected = expected[:max_stocks]
        result = target.read_symbols(self.test_symbol_file, max_stocks)
        self.assertEqual(expected, result, 'Target returned: {}'.format(result))

    def testDataSets(self):
        symbols = target.read_symbols(self.test_symbol_file)
        r_fn = None
        try:
            with tempfile.NamedTemporaryFile(delete=False) as r_file:
                r_fn = r_file.name
                target.make_train_cv_data_sets(symbols, 2, r_file)
            self.assertTrue(filecmp.cmp(self.expected_datasets_all, r_fn))
        finally:
            os.remove(r_fn)
            r_fn = None
        
    def testDataSets3(self):
        symbols = target.read_symbols(self.test_symbol_file)
        r_fn = None
        try:
            with tempfile.NamedTemporaryFile(delete=False) as r_file:
                r_fn = r_file.name
                target.make_train_cv_data_sets(symbols, 3, r_file)
            self.assertTrue(filecmp.cmp(self.expected_datasets_all3, r_fn))
        finally:
            os.remove(r_fn)
            r_fn = None
