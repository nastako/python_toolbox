# Copyright 2009-2012 Ram Rachum.
# This program is distributed under the MIT license.

'''Testing package for `exceptions.CuteBaseException`.'''

from python_toolbox import cute_testing

from python_toolbox.exceptions import CuteBaseException, CuteException


def test():
        
    try:
        raise CuteBaseException
    except BaseException, base_exception:
        assert base_exception.message == ''
    else:
        raise cute_testing.Failure
        
    try:
        raise CuteBaseException()
    except BaseException, base_exception:
        assert base_exception.message == ''
    else:
        raise cute_testing.Failure
        
        
    class MyBaseException(CuteBaseException):
        '''My hovercraft is full of eels.'''
        
        
    try:
        raise MyBaseException()
    except BaseException, base_exception:
        assert base_exception.message == '''My hovercraft is full of eels.'''
    else:
        raise cute_testing.Failure
        
    try:
        raise MyBaseException
    except BaseException, base_exception:
        assert base_exception.message == '''My hovercraft is full of eels.'''
    else:
        raise cute_testing.Failure