"""
Exceptions for Hadoop stream API emulator

@Author: Hideki Ikeda
Created: September 28, 2014
"""

class HSEException(Exception):
    """
    Base exception class for HadoopStreamEnulator class
    """
    pass


class HSEInputFormatterError(HSEException):
    """
    Raised when input formatter reported an error
    """
    def __init__(self, msg):
        self.msg = msg


class HSEOutputFormatterError(HSEException):
    """
    Raised when output formatter reported an error
    """
    def __init__(self, msg):
        self.msg = msg


class HSEMapperError(HSEException):
    """
    Raised when mapper reported an error
    """
    def __init__(self, msg):
        self.msg = msg


class HSEReducerError(HSEException):
    """
    Raised when reducer reported an error
    """
    def __init__(self, msg):
        self.msg = msg


class HSEInputPathError(HSEException):
    """
    Raised when input path is invalid
    """
    def __init__(self, msg):
        self.msg = msg


class HSEOutputPathError(HSEException):
    """
    Raised when output path already exists
    """
    def __init__(self, msg):
        self.msg = msg
