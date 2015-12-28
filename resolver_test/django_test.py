# Copyright (c) 2011 Resolver Systems Ltd.
# All Rights Reserved
#

from urlparse import urljoin

from mock import Mock

from resolver_test import ResolverTestMixins

import django
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpRequest, HttpResponseRedirect





class ResolverDjangoTestCase(django.test.TestCase, ResolverTestMixins):
    maxDiff = None

    def assert_redirects_to(self, response, redirect_url):
        self.assertTrue(isinstance(response, HttpResponseRedirect), "Response is not a redirect")
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response['Location'], redirect_url)


    def assert_login_required(self, view_to_call):
        self.owner = self.request.user = AnonymousUser()
        self.request.get_full_path = lambda: "my_path"
        self.request.build_absolute_uri = lambda: "my_path"

        response = view_to_call()

        self.assert_redirects_to(
            response,
            urljoin(settings.LOGIN_URL, '?next=my_path')
        )



class ResolverViewTestCase(ResolverDjangoTestCase):

    def setUp(self):
        self.user = User(username='cherie')
        self.user.save()

        self.request = HttpRequest()
        self.request.session = Mock()
        self.request.user = self.user

