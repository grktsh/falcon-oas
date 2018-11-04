# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from falcon import testing

from falcon_oas import Request


def test_host_url():
    req = Request(testing.create_environ(port=8080))

    assert req.host_url == 'http://' + testing.DEFAULT_HOST + ':8080'


def test_oas_query():
    req = Request(testing.create_environ())
    req.context['oas.parameters'] = {'query': {'q': 2}}

    assert req.oas_query == {'q': 2}


def test_oas_header():
    req = Request(testing.create_environ())
    req.context['oas.parameters'] = {'header': {'h': 2}}

    assert req.oas_header == {'h': 2}


def test_oas_cookie():
    req = Request(testing.create_environ())
    req.context['oas.parameters'] = {'cookie': {'c': 2}}

    assert req.oas_cookie == {'c': 2}


def test_oas_media():
    req = Request(testing.create_environ())
    req.context['oas.request_body'] = {'x': 2}

    assert req.oas_media == {'x': 2}


def test_oas_user():
    req = Request(testing.create_environ())
    req.context['oas.user'] = 'user'

    assert req.oas_user == 'user'
