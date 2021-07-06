# Copyright (c) 2017 PythonAnywhere LLP.
# All Rights Reserved
#

from urllib.parse import urljoin
from unittest.mock import Mock

from resolver_test import ResolverTestMixins

import django
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpRequest




class ResolverDjangoTestCase(django.test.TestCase, ResolverTestMixins):
    maxDiff = None



usernumber = 0

class ResolverViewTestCase(ResolverDjangoTestCase):

    def setUp(self):
        global usernumber
        self.user = User.objects.create(username='cherie{}'.format(usernumber))
        usernumber += 1

        self.request = HttpRequest()
        self.request.session = Mock()
        self.request.user = self.user

        self.client.force_login(self.user)


    def assert_login_required(self, view_to_call):
        self.owner = self.request.user = AnonymousUser()
        self.request.get_full_path = lambda: "my_path"
        self.request.build_absolute_uri = lambda: "my_path"

        response = view_to_call()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            urljoin(settings.LOGIN_URL, '?next=my_path')
        )

