from distutils.core import setup

setup(
    name = 'chelmbigstock',
    packages = ['chelmbigstock'],
    version = '0.1',
    description = 'Stock analyzer',
    author = 'Chelmsford Big Data Study Group',
    author_email = 'mike@75design.com',
    url = 'https://github.com/mikec964/chelmbigstock',

    classifiers = [
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Development Status :: Pre-alpha',
        'Intended Audience :: Developers',
    ],

    long_description = """\
Chelmsford Big Stock
--------------------

At the moment, this program analyzes a few stock histories and calculates their alpha. Or something.
"""
 )
