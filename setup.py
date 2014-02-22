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
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Topic :: System :: Distributed Computing',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],

    long_description = open('README.rst').read(),
 )
