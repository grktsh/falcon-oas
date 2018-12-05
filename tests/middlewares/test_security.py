# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
import pytest
from falcon import testing

from falcon_oas.factories import create_spec_from_dict
from falcon_oas.middlewares.security import _get_api_key
from falcon_oas.middlewares.security import get_security_schemes
from falcon_oas.middlewares.security import SecurityMiddleware
from tests.helpers import yaml_load_dedent

USER = object()
RESOURCE = object()


def session_user_loader(value):
    return {'user': USER, 'none': None, '1': True, '0': False}[value]


security_schemes = {
    'session': (
        {'type': 'apiKey', 'name': 'session', 'in': 'cookie'},
        session_user_loader,
    ),
    'api_key': (
        {'type': 'apiKey', 'name': 'X-API-Key', 'in': 'header'},
        session_user_loader,
    ),
    'http': ({'type': 'http', 'scheme': 'basic'}, None),
    'oauth2': ({'type': 'oauth2', 'flows': {}}, None),
    'openIdConnect': ({'type': 'openIdConnect', 'openIdConnectUrl': ''}, None),
}


def test_undocumented_request():
    req = falcon.Request(testing.create_environ())
    req.uri_template = req.path
    resp = falcon.Response()

    spec = create_spec_from_dict({'paths': {}})
    middleware = SecurityMiddleware(spec, security_schemes)
    middleware.process_resource(req, resp, RESOURCE, {})

    assert req.context == {}


def test_without_security():
    req = falcon.Request(testing.create_environ(path='/path'))
    req.uri_template = req.path
    resp = falcon.Response()

    spec = create_spec_from_dict({'paths': {'/path': {'get': {}}}})
    middleware = SecurityMiddleware(spec, security_schemes)
    middleware.process_resource(req, resp, RESOURCE, {})

    assert req.context == {}


@pytest.mark.parametrize(
    'headers,security,context',
    [
        (
            {'Cookie': str('session=user')},
            [{'session': []}],
            {'oas.user': USER},
        ),
        ({'Cookie': str('session=1')}, [{'session': []}], {}),
        (
            {'Cookie': str('session=user'), 'X-API-Key': '1'},
            [{'session': [], 'api_key': []}],
            {'oas.user': USER},
        ),
        (
            {'Cookie': str('session=user'), 'X-API-Key': '0'},
            [{'session': []}, {'api_key': []}],
            {'oas.user': USER},
        ),
        (
            {'Cookie': str('session=0'), 'X-API-Key': 'user'},
            [{'session': []}, {'api_key': []}],
            {'oas.user': USER},
        ),
    ],
)
def test_success(headers, security, context):
    req = falcon.Request(testing.create_environ(path='/path', headers=headers))
    req.uri_template = req.path
    resp = falcon.Response()

    spec_dict = {'paths': {'/path': {'get': {'security': security}}}}
    spec = create_spec_from_dict(spec_dict)
    middleware = SecurityMiddleware(spec, security_schemes)
    middleware.process_resource(req, resp, RESOURCE, {})

    assert req.context == context


@pytest.mark.parametrize(
    'headers,security',
    [
        ({'Cookie': str('')}, [{'session': []}]),
        ({'Cookie': str('session=none')}, [{'session': []}]),
        ({'Cookie': str('session=0')}, [{'session': []}]),
        (
            {'Cookie': str('session=0'), 'X-API-Key': 'user'},
            [{'session': [], 'api_key': []}],
        ),
        (
            {'Cookie': str('session=user'), 'X-API-Key': '0'},
            [{'session': [], 'api_key': []}],
        ),
    ],
)
def test_forbidden(headers, security):
    req = falcon.Request(testing.create_environ(path='/path', headers=headers))
    req.uri_template = req.path
    resp = falcon.Response()

    spec_dict = {'paths': {'/path': {'get': {'security': security}}}}
    spec = create_spec_from_dict(spec_dict)
    middleware = SecurityMiddleware(spec, security_schemes)

    with pytest.raises(falcon.HTTPForbidden):
        middleware.process_resource(req, resp, RESOURCE, {})


@pytest.mark.parametrize('key', ['http', 'oauth2', 'openIdConnect'])
def test_unsupported_type(key):
    req = falcon.Request(testing.create_environ(path='/path'))
    req.uri_template = req.path
    resp = falcon.Response()

    spec_dict = {'paths': {'/path': {'get': {'security': [{key: []}]}}}}
    spec = create_spec_from_dict(spec_dict)
    middleware = SecurityMiddleware(spec, security_schemes)
    middleware.process_resource(req, resp, RESOURCE, {})

    assert req.context == {}


def test_get_api_key_cookie():
    req = falcon.Request(
        testing.create_environ(headers={'Cookie': str('session=value')})
    )
    assert _get_api_key(req, 'cookie', 'session') == 'value'


def test_get_api_key_header():
    req = falcon.Request(
        testing.create_environ(headers={'X-API-Key': 'value'})
    )
    assert _get_api_key(req, 'header', 'X-API-Key') == 'value'


def test_get_api_key_query():
    req = falcon.Request(
        testing.create_environ(query_string='X-API-Key=value')
    )
    assert _get_api_key(req, 'query', 'X-API-Key') == 'value'


@pytest.mark.parametrize(
    'location,error',
    [
        ('cookie', KeyError),
        ('header', falcon.HTTPMissingHeader),
        ('query', KeyError),
    ],
)
def test_get_api_key_missing(location, error):
    req = falcon.Request(testing.create_environ())
    with pytest.raises(error):
        _get_api_key(req, location, 'X-API-Key')


def test_get_security_schemes():
    spec_dict = yaml_load_dedent(
        """\
        components:
          securitySchemes:
            session:
              type: apiKey
              name: session
              in: cookie
              x-user-loader: middlewares.test_security:session_user_loader
        """
    )
    result = get_security_schemes(spec_dict, base_module='tests')
    assert result == {
        'session': (
            spec_dict['components']['securitySchemes']['session'],
            session_user_loader,
        )
    }


def test_get_security_schemes_none():
    assert get_security_schemes({}) is None
