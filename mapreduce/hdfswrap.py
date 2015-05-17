'''
File-like classes for HDFS access through webHDFS

Created on May 12, 2015
@author: Hideki Ikeda
'''

import tempfile
import requests as req

class HDFSWrapper(object):
    '''
    Base class for file-like classes to access HDFS through webHDFS
    Child classes: HDFSWrapperWrite, HDFSWrapperRead
    '''

    _op = 'op'
    _op_ls = 'LISTSTATUS'
    _p_user = 'user.name'

    def __init__(self, host, port, path, user = None):
        self._url = 'http://{}:{}/webhdfs/v1{}{}'.format(
                host, port, ('' if path[0] == '/' else '/'), path)
        self._user = user


class HDFSWrapperWrite(HDFSWrapper):
    '''
    File-like class to write a file to HDFS through webHDFS
    Constructor parameters:
        host:   name/IP address of name node
        port:   port No. of webHDFS
        path:   absolute path to the file to access on HDFS
        append: if True, appends data to the 'path'. If 'path' doesn't exist,
                just creates a file.
                if False, overwrites the existing content.
                Default: False (overwrite)
                Note: the APPEND operation may not be enabled on HDFS.
                      If not enabled, the wrapper raises IOError.
        user:   specifies the user name to access HDFS. This wrapper doesn't
                support security option.
    '''

    _op_append = 'APPEND'
    _op_create = 'CREATE'

    def __init__(self, host, port, path, append = False, user = None):
        super(HDFSWrapperWrite, self).__init__(host, port, path, user)
        self._append = append
        self._f_temp = None

    def _make_params(self, org_param):
        # internal method to create a parameter dict for webHDFS command
        # Note: this method changes the original parameter dict!
        if self._user is not None:
            org_param[self._p_user] = self._user
        return org_param

    def open(self):
        '''
        Open a channel to HDFS and returns a file-like object.
        '''
        # if we are in append but file doesn't exists, we will create
        # a new file
        if self._append:
            # check see if the file exists
            ps = self._make_params({ self._op: self._op_ls })
            r = req.get(self._url, params=ps)
            if r.status_code == 200:
                # the file already exists; do nothing
                pass
            elif r.status_code == 404:
                # the file doesn't exist yet; we will create it later
                self._append = False
            else:
                raise IOError('{} {}:{} {}'.format(
                    r.status_code, r.reason, r.url, r.content))

        # set up parameters for write
        if self._append:
            self._req = req.post
            self._params = self._make_params({self._op: self._op_append})
        else:
            self._req = req.put
            self._params = self._make_params(
                    {self._op: self._op_create, 'overwrite':'true'})

        # set up temporary file to store user input
        self._f_temp = tempfile.TemporaryFile()

        return self

    def close(self):
        '''
        Send out the content to HDFS and close the channel to HDFS
        '''
        if self._f_temp is not None:
            # send out the user input to HDFS
            try:
                r = self._req(self._url, params=self._params,
                            allow_redirects=False)

                if r.status_code == 307:
                    self._f_temp.flush();
                    self._f_temp.seek(0)
                    r = self._req(r.headers['location'], data=self._f_temp)

                if r.status_code >= 300:
                    raise IOError('{} {}:{} {}'.format(
                        r.status_code, r.reason, r.url, r.content))
            finally:
                self._f_temp.close()

    def write(self, data):
        # save user input to the temp file
        self._f_temp.write(data)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.close()
        else:
            # we are exiting due to an exception; don't send the content
            # to HDFS. Just close the temp file
            if self._f_temp is not None:
                self._f_temp.close()

        return False
