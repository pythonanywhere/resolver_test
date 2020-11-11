# Copyright (c) 2011 Resolver Systems Ltd.
# All Rights Reserved
#

import unittest
from datetime import timedelta
from unittest.mock import call, MagicMock


class ResolverTestMixins(object):

    def assertCalledOnce(self, mock, *args, **kwargs):
        if mock.call_args_list == []:
            self.fail('Not called')
        self.assertListEqual(mock.call_args_list, [call(*args, **kwargs)])


    def assert_decorated_with(self, fn, decorator):
        self.assertIn(decorator.__name__, fn.decorated_by)


    def assert_datetime_approximately_equals(self, actual, expected, minutes_leeway=10):
        self.assertTrue(
            expected - timedelta(minutes=minutes_leeway) <= actual <= expected + timedelta(minutes=minutes_leeway),
            "%r is not within %s minutes of %r" % (actual, minutes_leeway, expected)
        )



class ResolverTestCase(unittest.TestCase, ResolverTestMixins):
    maxDiff = None



def die(exception=None):
    if exception is None:
        exception = AssertionError('die called')

    def inner_die(*_, **__):
        raise exception
    return inner_die


def is_iterable(seq):
    return hasattr(seq, "__iter__")


def create_mock_context_manager():
    mock_cm_class = MagicMock()
    mock_cm = mock_cm_class.return_value
    mock_cm.__enter__.return_value = mock_cm

    def check_used_as_context_manager():
        return mock_cm.__enter__.called is True and mock_cm.__exit__.called is True

    mock_cm.check_used_as_context_manager = check_used_as_context_manager
    return mock_cm_class

