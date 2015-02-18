'''
Created on Oct 24, 2014

@author: Hideki Ikeda
'''

import os
import sys
import filecmp
import unittest
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
import preprocess as target


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
        gen = target.data_type_generator()
        self.assertEqual(gen.next(), 'TR')
        self.assertEqual(gen.next(), 'CV')
        self.assertEqual(gen.next(), 'TR')
        self.assertEqual(gen.next(), 'CV')

    def testReadSymbols(self):
        with open(self.test_symbol_file, 'r') as f_test:
            expected = [ line.strip() for line in f_test ]
        result = target.read_symbols(self.test_symbol_file)
        self.assertEqual(expected, result, 'Target returned: {}'.format(result))

    def testPreprocessAll(self):
        symbols = target.read_symbols(self.test_symbol_file)
        target.preprocess(symbols, self.data_dir, self.result_all)
        self.assertTrue(filecmp.cmp(self.expected_all, self.result_all))

    def testPrerpecessTwo(self):
        symbols = target.read_symbols(self.test_symbol_file)
        target.preprocess(symbols, self.data_dir, self.result_two, 2)
        self.assertTrue(filecmp.cmp(self.expected_two, self.result_two))

    def testPrerpecessBad(self):
        symbols = target.read_symbols(self.test_bad_symbol_file)
        target.preprocess(symbols, self.data_dir, self.result_bad)
        self.assertTrue(filecmp.cmp(self.expected_bad, self.result_bad))
