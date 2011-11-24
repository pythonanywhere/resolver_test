# Copyright (c) 2011 Resolver Systems Ltd.
# All Rights Reserved
#

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from mock import call


class ResolverTestMixins(object):
    def assertCalledOnce(self, mock, *args, **kwargs):
        if mock.call_args_list == []:
            self.fail('Not called')
        self.assertEquals(mock.call_args_list, [call(*args, **kwargs)])


    def assert_decorated_with(self, fn, decorator):
        self.assertIn(decorator.__name__, fn.decorated_by)


    def assert_decorated_with(self, fn, decorator):
        self.assertIn(decorator.__name__, fn.decorated_by)



class ResolverTestCase(unittest.TestCase, ResolverTestMixins):
    maxDiff = None



def die(exception=None):
    if exception is None:
        exception = AssertionError('die called')
    def inner_die(*_):
        raise exception
    return inner_die

def is_iterable(seq):
    return hasattr(seq, "__iter__")

