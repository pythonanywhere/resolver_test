# Copyright (c) 2011 Resolver Systems Ltd.
# All Rights Reserved
#

from os.path import dirname, join
import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest
from urlparse import urljoin

from mock import call, MagicMock, Mock

import django
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.db import connections
from django.http import HttpRequest, HttpResponseRedirect
from django.test.simple import DjangoTestSuiteRunner


class ResolverTestMixins(object):
    def assertCalledOnce(self, mock, *args, **kwargs):
        if mock.call_args_list == []:
            self.fail('Not called')
        self.assertEquals(mock.call_args_list, [call(*args, **kwargs)])


class ResolverTestCase(unittest.TestCase, ResolverTestMixins):
    maxDiff = None


class ResolverTestSuiteRunner(DjangoTestSuiteRunner):

    def get_ignored_tests(self):
        return []


    def run_suite(self, suite, **kwargs):
        ignored_tests = self.get_ignored_tests()
        filtered_suite = unittest.TestSuite()
        for test in suite:
            if hasattr(test, 'id') and test.id() not in ignored_tests:
                filtered_suite.addTest(test)
        return DjangoTestSuiteRunner.run_suite(self, filtered_suite, **kwargs)



def die(exception=None):
    if exception is None:
        exception = AssertionError('die called')
    def inner_die(*_):
        raise exception
    return inner_die

def is_iterable(seq):
    return hasattr(seq, "__iter__")



class ResolverDjangoTestMixins(ResolverTestMixins):

    def get_value_rendered_with(self, mock_render, argname):
        self.assertEquals(len(mock_render.call_args_list), 1)

        (_, args_dict), _ = mock_render.call_args

        self.assertTrue(argname in args_dict, "%s not passed to template" % (argname,))
        return args_dict[argname]


    def assertRenderedWith(self, mock_render, argname, expected_value):
        rendered_value = self.get_value_rendered_with(mock_render, argname)
        if is_iterable(expected_value) and not isinstance(expected_value, MagicMock):
            self.assertItemsEqual(rendered_value, expected_value)
        else:
            self.assertEquals(rendered_value, expected_value)


    def assert_render_template_was(self, mock_render, expected_template):
        self.assertEquals(len(mock_render.call_args_list), 1)

        (actual_template, _), _ = mock_render.call_args
        self.assertEquals(actual_template, expected_template)


    def assert_context_instance_was_correct(self, mock_render, mock_request_context_class, request):
        self.assertEquals(len(mock_render.call_args_list), 1)

        __, kwargs = mock_render.call_args
        self.assertEquals(kwargs['context_instance'], mock_request_context_class.return_value)
        self.assertCalledOnce(mock_request_context_class, request)


    def assert_redirects_to(self, response, redirect_url):
        self.assertTrue(isinstance(response, HttpResponseRedirect), "Response is not a redirect")
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], redirect_url)


    def assert_login_required(self, view_to_call):
        self.owner = self.request.user = AnonymousUser()
        self.request.get_full_path = lambda : "my_path"
        self.request.build_absolute_uri = lambda : "my_path"

        response = view_to_call()

        self.assert_redirects_to(response,
                urljoin(settings.LOGIN_URL, '?next=my_path')
        )


    def assert_decorated_with(self, fn, decorator):
        self.assertIn(decorator.__name__, fn.decorated_by)



class ResolverDjangoTestCase(django.test.TestCase, unittest.TestCase, ResolverDjangoTestMixins):
    maxDiff = None


class ResolverViewTestCase(ResolverDjangoTestCase):

    def setUp(self):
        self.user = User(username='cherie')
        self.user.save()

        self.request = HttpRequest()
        self.request.session = Mock()
        self.request.user = self.user




TEST_CLASSES = (
    unittest.TestCase,
    django.test.TestCase,
    ResolverTestCase,
    ResolverDjangoTestCase
)

def assert_security_classes_exist(test, module_name, excludes=None):
    '''
    ensure that, as a minimum sanity check, each non-security test class in
    this module has an associated security test class.
    '''
    test_classes = [
        name for name, item in sys.modules[module_name].__dict__.iteritems()
        if isinstance(item, type) and issubclass(item, TEST_CLASSES)
        and not item in TEST_CLASSES
    ]
    regular_test_classes = [
        name for name in test_classes
        if not name.endswith('SecurityTest')
    ]
    if excludes is None:
        excludes = []
    for name in regular_test_classes:
        if name not in excludes:
            test.assertTrue(
                name[:-4] + 'SecurityTest' in test_classes,
                "class %s doesn't have a security test. "
                "Use user page security test as template" % (name,)
            )

