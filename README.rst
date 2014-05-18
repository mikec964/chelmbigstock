#############
chelmbigstock
#############

This application is being created by the Chelmsford Big Data Study Group. We keep a wiki with notes about this project and our meetings at:
https://github.com/mikec964/chelmbigstock.

Usage
#####
1. You should specify which stocks you want to use. Edit the list
in stock_symbols.txt and put a symbol on each line.

2. Run data_download.py; this will load all of the data into the data folder.

3. Run chelmbigstock.py; This will calculate the results.


Features
########


Planned Features
################
Requires (Try `pip install <name>` or see the wiki.):
* numpy
* sklearn
* LearningData

Testing
#######
From the tests folder, use::

    python -m unittest discover -p '*tests.py'

From the chelmbigstock folder, you can test the docs for a module with::

    python3 -m doctest -v data_download.py
