#

'''
May,08, 2014
@author Hideki Ikeda
Unit test for the LinearAdapter class in stock_value.py
'''

import os
import sys
from datetime import date, datetime, timedelta
import shutil
import unittest
from sklearn import linear_model

sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
from chelmbigstock import stock_value


class TestLinearAdapter(unittest.TestCase):
    _e = 1e-6                       # tolerance
    _test_LR = [                    # test data for linear regression
            [
                [0, 1, 3],
                [0, 1, 3],
                [5.5], [5.5]
            ],
            [
                [1, 3, 4, 5, 9],
                [2, 5, 8, 7, 10],
                [5.5], [7.4375]
            ]
        ]

    _test_RR = [                    # test data for Ridge regression with alpha = 0.5
            [
                [0, 1, 3],
                [0, 1, 3],
                [5.5], [5.09677419]
            ],
            [
                [1, 3, 4, 5, 9],
                [2, 5, 8, 7, 10],
                [5.5], [7.42296919]
            ]
        ]


    def equal_floats(self, l1, l2):
        if len(l1) != len(l2):
            return False
        for i in range(0, len(l1)):
            if abs((l1[i] - l2[i])/l1[i]) >= self._e:
                return False
        return True


    def test_linear_regression(self):
        clf = linear_model.LinearRegression()
        predictor = stock_value.LinearAdapter(clf)
        for x, y, ex, ey in self._test_LR:
            predictor.fit(x, y)
            self.assertTrue(self.equal_floats(ey, predictor.predict([ex])))

    def test_ridge_regression(self):
        clf = linear_model.Ridge(alpha = 0.5)
        predictor = stock_value.LinearAdapter(clf)
        for x, y, ex, ey in self._test_RR:
            predictor.fit(x, y)
            self.assertTrue(self.equal_floats(ey, predictor.predict([ex])))



if __name__ == "__main__":
    unittest.main()
