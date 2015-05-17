#!/usr/bin/env python
'''
Created on May 9, 2015

@author: Hideki Ikeda
'''

import os
import sys
import json
import unittest
import requests as req
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..'))
import hdfswrap as target


class DummyError(BaseException):
    '''
    Dummy exeption class for intentional exception tests
    '''
    def __init__(self, msg):
        super(DummyError, self).__init__(msg)


class TestHDFSWrapper(unittest.TestCase):
    '''
    Unit tests for HDFSWrapper
    '''
    _host = 'suizei'
    _port = 50070
    _user = 'hduser'
    _test_dir = '/user/{}/unittest'.format(_user)
    _op_list = 'LISTSTATUS'
    _op_mkdir = 'MKDIRS'
    _op_create = 'CREATE'
    _op_read = 'OPEN'
    _op_delete = 'DELETE'

    @classmethod
    def setUpClass(cls):
        '''
        Make sure HDFS is up and running; create a common test directory
        '''
        # set up common data
        cls._header = 'http://{}:{}/webhdfs/v1{}'.format(
                cls._host, cls._port, cls._test_dir)
        ps = {'user.name':cls._user, 'op':cls._op_list}
        r = req.get(cls._header, params=ps)

        # make sure HDFS is up and running and the dir for unit test exists
        if r.status_code == 404: # Not Found
            ps = {'user.name':cls._user, 'op':cls._op_mkdir}
            r = req.put(cls._header, params=ps)
        if r.status_code != 200:
            raise IOError('{} {}:{} {}'.format(
                r.status_code, r.reason, r.url, r.content))

    @classmethod
    def tearDownClass(cls):
        '''
        Delete the unit test dir
        '''
        ps = {'user.name':cls._user, 'op':cls._op_delete, 'recursive':'true'}
        r = req.delete(cls._header, params=ps)
        if r.status_code not in [200]:
            raise IOError('{} {}:{}'.format(r.status_code, r.reason, req_url))

    def writeFile(self, filename, data):
        '''
        Create a file on HDFS
        Parameters:
            filename: the name of file to be created on HDFS
            data:     the content of the new file: Dictionary, bytes,
                      or file-like object
        '''
        url = '/'.join([self._header, filename])
        ps = {'user.name':self._user, 'op':self._op_create, 'overwrite':'true'}
        r = req.put(url, params=ps, allow_redirects=False)
        if r.status_code != 307:
            raise IOError('{} {}:{}'.format(r.status_code, r.reason, r.url))

        r = req.put(r.headers['location'], data=data)
        if r.status_code != 201:
            raise IOError('{} {}:{}'.format(r.status_code, r.reason, r.url))

    def readFile(self, filename):
        '''
        read a file on HDFS
        Parameters:
            filename: the name of file to be deleted
        Return: ontent in string
        '''
        url = '/'.join([self._header, filename])
        ps = {'user.name':self._user, 'op':self._op_read}
        r = req.get(url, params=ps, allow_redirects=False)
        if r.status_code != 307:
            raise IOError('{} {}:{}'.format(r.status_code, r.reason, r.url))

        r = req.get(r.headers['location'])
        if r.status_code != 200:
            raise IOError('{} {}:{}'.format(r.status_code, r.reason, r.url))
        
        return r.content

    def deleteFile(self, filename):
        '''
        Delete a file on HDFS
        Parameters:
            filename: the name of file to be deleted
        '''
        url = '/'.join([self._header, filename])
        ps = {'user.name':self._user, 'op':self._op_delete}
        r = req.delete(url, params=ps)

    def testCreate(self):
        '''
        Create a new file
        '''
        # file name to be created on HDFS
        hdfs_file = 'deleteme.txt'
        hdfs_path = '/'.join([self._test_dir, hdfs_file])

        # file name of source on local
        src_file = os.path.join('data', 'hdfsmrg.txt')

        wrap = target.HDFSWrapperWrite(self._host, self._port,
                hdfs_path, user=self._user)
        try:
            with open(src_file, 'r') as fh_src, wrap.open() as fh_hdfs:
                for line in fh_src:
                    fh_hdfs.write(line)
            # compare srouce and result
            cont_hdfs = self.readFile(hdfs_file)
            with open(src_file, 'r') as fh_exp:
                cont_exp = fh_exp.read()
            self.assertEqual(cont_exp, cont_hdfs)
        finally:
            self.deleteFile(hdfs_file)

    def testAppend(self):
        '''
        Append content to an existing file on HDFS
        '''
        # create a base file on HDFS
        hdfs_file = 'deleteme.txt'
        src_file = os.path.join('data', 'hdfssrc.txt')
        with open(src_file, 'r') as fh_org:
            self.writeFile(hdfs_file, fh_org)

        try:
            # append hdfsapp.txt to the file on HDFS
            hdfs_path = '/'.join([self._test_dir, hdfs_file])
            wrap = target.HDFSWrapperWrite(self._host, self._port,
                    hdfs_path, append=True, user=self._user)
            apnd_file = os.path.join('data', 'hdfsapp.txt')
            with open(apnd_file) as fh_apnd, wrap.open() as fh_hdfs:
                for line in fh_apnd:
                    fh_hdfs.write(line)

            # make sure the file on HDFS has the same content to src_file
            cont_hdfs = self.readFile(hdfs_file)
            exp_file = os.path.join('data', 'hdfsmrg.txt')
            with open(exp_file, 'r') as fh_exp:
                cont_org = fh_exp.read()
            self.assertEqual(cont_org, cont_hdfs)
        finally:
            self.deleteFile(hdfs_file)

    def testOverwrite(self):
        '''
        Overwrite an existing file on HDFS
        '''
        # create a base file on HDFS to be overwritten
        hdfs_file = 'deleteme.txt'
        org_file = os.path.join('data', 'hdfssrc.txt')
        with open(org_file, 'r') as fh_org:
            self.writeFile(hdfs_file, fh_org)

        try:
            # overwrite the file on HDFS with local src_file
            hdfs_path = '/'.join([self._test_dir, hdfs_file])
            wrap = target.HDFSWrapperWrite(self._host, self._port,
                    hdfs_path, user=self._user)
            src_file = os.path.join('data', 'hdfsapp.txt')
            with open(src_file) as fh_src, wrap.open() as fh_hdfs:
                for line in fh_src:
                    fh_hdfs.write(line)

            # make sure the file on HDFS has the same content to src_file
            cont_hdfs = self.readFile(hdfs_file)
            with open(src_file, 'r') as fh_org:
                cont_org = fh_org.read()
            self.assertEqual(cont_org, cont_hdfs)
        finally:
            self.deleteFile(hdfs_file)

    def testExitOnException(self):
        '''
        Try to create a new file but exit on an exception
        On an exception, the wrapper doesn't make a file on HDFS
        '''
        # file name to be created on HDFS
        hdfs_file = 'deleteme.txt'
        hdfs_path = '/'.join([self._test_dir, hdfs_file])

        # file name of source on local
        src_file = os.path.join('data', 'hdfsmrg.txt')

        wrap = target.HDFSWrapperWrite(self._host, self._port,
                hdfs_path, user=self._user)
        try:
            with open(src_file, 'r') as fh_src, wrap.open() as fh_hdfs:
                line = fh_src.readline()
                fh_hdfs.write(line)
                raise DummyError('testExitOnException') # intentional exception
        except DummyError as e:
            pass    # intentional exception; just ignore
        finally:
            self.deleteFile(hdfs_file)

        # make sure the hdfs file doesn't exist
        url = '/'.join([self._header, hdfs_path])
        ps = {'user.name':self._user, 'op':self._op_list}
        r = req.get(url, params=ps)
        
        self.assertEqual(r.status_code, 404)


if __name__ == '__main__':
    unittest.main()
