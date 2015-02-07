#!/usr/bin/env python3
'''
Created on Feb 7, 2015

@author: Hideki Ikeda
'''

import os
import sys
import filecmp
import unittest
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
import download_data as target


class TestDownload(unittest.TestCase):
    '''
    Unit tests for download_data
    '''
    test_symbol_path = os.path.join('data', 'test_symbols.txt')

    def test_read_symbols_all(self):
        expected = [ 'SYMBOL1', 'SYMBOL2', 'SYMBOL3', 'SYMBOL4' ]
        result = target.read_symbols(self.test_symbol_path)
        self.assertEqual(expected, result)

    def test_read_symbols_2(self):
        expected = [ 'SYMBOL1', 'SYMBOL2' ]
        result = target.read_symbols(self.test_symbol_path, 2)
        self.assertEqual(expected, result)

    def test_read_symbols_0(self):
        expected = []
        result = target.read_symbols(self.test_symbol_path, 0)
        self.assertEqual(expected, result)

    def test_read_symbols_negative(self):
        expected = []
        result = target.read_symbols(self.test_symbol_path, -1)
        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
