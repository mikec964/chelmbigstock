#!/usr/bin/env python

'''
Created on Oct 24, 2014

@author: Hideki Ikeda
'''

import os
import sys
import tempfile
import filecmp
import datetime as dt
import unittest
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
import mkmropt as target


class TestPreprocess(unittest.TestCase):
    ''')

    def testExtractDates(self):
        expected = [ dt.date(2015, 1, 2)

    Unit tests
    '''

    @classmethod
    def setUpClass(cls):
        cls.data_dir = 'data'
        cls.test_symbol_file = os.path.join(cls.data_dir, 'test_symbols.txt')
        cls.expected_all = os.path.join(cls.data_dir, 'expected_all.csv')
        cls.result_all = os.path.join(cls.data_dir, 'result_all.csv')
        cls.expected_two = os.path.join(cls.data_dir, 'expected_two.csv')
        cls.result_two = os.path.join(cls.data_dir, 'result_two.csv')
        cls.expected_datasets_all = os.path.join(cls.data_dir,
                'expected_datasets_all.txt')
        cls.expected_datasets_all3 = os.path.join(cls.data_dir,
                'expected_datasets_all3.txt')
        cls.test_mktcal = os.path.join(cls.data_dir, 'test_mktcal.csv')

        cls.test_bad_symbol_file = os.path.join(cls.data_dir, 'test_symbols_with_bad.txt')
        cls.expected_bad = os.path.join(cls.data_dir, 'expected_two.csv') # reuse the result
        cls.result_bad = os.path.join(cls.data_dir, 'result_bad.csv')

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.result_all):
            os.remove(cls.result_all)
        if os.path.exists(cls.result_two):
            os.remove(cls.result_two)
        if os.path.exists(cls.result_bad):
            os.remove(cls.result_bad)

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
                target.make_symbol_sets(symbols, 2, r_file)
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
                target.make_symbol_sets(symbols, 3, r_file)
            self.assertTrue(filecmp.cmp(self.expected_datasets_all3, r_fn))
        finally:
            os.remove(r_fn)
            r_fn = None

    def testReadCalendar(self):
        expected = [ dt.date(2015, 1, 2)
                    ,dt.date(2015, 1, 5)
                    ,dt.date(2015, 1, 6)
                    ,dt.date(2015, 1, 7)
                    ,dt.date(2015, 1, 8)
                    ,dt.date(2015, 1, 9)
                    ,dt.date(2015, 1,12)
                    ,dt.date(2015, 1,13)
                    ,dt.date(2015, 1,14)
                    ,dt.date(2015, 1,15)
                    ,dt.date(2015, 1,16)
                    ,dt.date(2015, 1,20)
                    ,dt.date(2015, 1,21)
                    ,dt.date(2015, 1,22)
                    ,dt.date(2015, 1,23)
                    ,dt.date(2015, 1,26)
                    ,dt.date(2015, 1,27)
                    ,dt.date(2015, 1,28)
                    ,dt.date(2015, 1,29)
                    ,dt.date(2015, 1,30)
                   ]
        result = target.read_calendar(self.test_mktcal)
        self.assertEqual(expected, result)

    def testExtractDatesExeption(self):
        cal = [ dt.date(2015, 1, 2), dt.date(2015, 1, 5) ]
        first = dt.date(2015, 1, 3)

        # invalid train_days
        self.assertRaises(ValueError, target.extract_dates, cal, first, 0, 1)
        # invalid train_inc
        self.assertRaises(ValueError, target.extract_dates, cal, first, 2, 0)

    def testExtractDatesNone(self):
        cal = [ dt.date(2015, 1, 2), dt.date(2015, 1, 5), dt.date(2015, 1, 6) ]

        # the first date out of range
        first = dt.date(2015, 1, 7)
        self.assertIsNone(target.extract_dates(cal, first, 2, 1),
                'first date out of range')

        # the last date out of range
        first - dt.date(2015, 1, 2)
        self.assertIsNone(target.extract_dates(cal, first, 3, 1),
                'last date out of range')

    def testExtractDates(self):
        cal = [ dt.date(2015, 1, 2)
               ,dt.date(2015, 1, 5)
               ,dt.date(2015, 1, 6)
               ,dt.date(2015, 1, 7)
               ,dt.date(2015, 1, 8)
               ,dt.date(2015, 1, 9)
               ,dt.date(2015, 1,12)
               ,dt.date(2015, 1,13)
               ,dt.date(2015, 1,14)
               ,dt.date(2015, 1,15)
               ,dt.date(2015, 1,16)
               ,dt.date(2015, 1,20)
               ,dt.date(2015, 1,21)
               ,dt.date(2015, 1,22)
               ,dt.date(2015, 1,23)
               ,dt.date(2015, 1,26)
               ,dt.date(2015, 1,27)
               ,dt.date(2015, 1,28)
               ,dt.date(2015, 1,29)
               ,dt.date(2015, 1,30)
              ]
        # on date
        first = dt.date(2015, 1, 5)
        days = 10
        inc = 3
        expected = [ cal[1]
                    ,cal[4]
                    ,cal[7]
                    ,cal[10]
                   ]
        result = target.extract_dates(cal, first, days, inc)
        self.assertEqual(expected, result, 'On date ' + str(result))

        # off date + very last in cal
        first = dt.date(2015, 1, 18)
        days = 9
        inc = 2
        expected = [ cal[11]
                    ,cal[13]
                    ,cal[15]
                    ,cal[17]
                    ,cal[19]
                   ]
        result = target.extract_dates(cal, first, days, inc)
        self.assertEqual(expected, result,
                'Off date + very last in cal' + str(result))

