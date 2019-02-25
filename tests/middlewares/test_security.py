# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
import pytest
from falcon import testing

from falcon_oas.extensions import FALCON_OAS_IMPLEMENTOR
from falcon_oas.middlewares.operation import OperationMiddleware
from falcon_oas.middlewares.security import get_security_schemes
from falcon_oas.middlewares.security import SecurityMiddleware
from falcon_oas.oas.spec import create_spec_from_dict
from tests.helpers import yaml_load_dedent

user = object()


def session_user_loader(value, scopes, req):
    if value is None:
        return None
    return {'user': user, 'none': None, '1': True, '0': False}[value]


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


def create_app(spec_dict):
    spec = create_spec_from_dict(spec_dict)
    app = falcon.API(
        middleware=[
            OperationMiddleware(spec),
            SecurityMiddleware(security_schemes),
        ]
    )
    return app


def test_undocumented_request(resource):
    app = create_app({'paths': {}})
    app.add_route('/undocumented', resource)

    client = testing.TestClient(app)
    response = client.simulate_get(path='/undocumented')

    assert response.status == falcon.HTTP_OK

    req = resource.captured_req
    assert 'oas.user' not in req.context


def test_without_security(resource):
    app = create_app({'paths': {'/path': {'get': {}}}})
    app.add_route('/path', resource)

    client = testing.TestClient(app)
    client.simulate_get(path='/path')

    req = resource.captured_req
    assert 'oas.user' not in req.context


@pytest.mark.parametrize(
    'headers,security',
    [
        ({'Cookie': str('session=user')}, [{'session': []}]),
        (
            {'Cookie': str('session=user'), 'X-API-Key': str('1')},
            [{'session': [], 'api_key': []}],
        ),
        (
            {'Cookie': str('session=user'), 'X-API-Key': str('0')},
            [{'session': []}, {'api_key': []}],
        ),
        (
            {'Cookie': str('session=0'), 'X-API-Key': str('user')},
            [{'session': []}, {'api_key': []}],
        ),
    ],
)
def test_success(headers, security, resource):
    spec_dict = {'paths': {'/path': {'get': {'security': security}}}}
    app = create_app(spec_dict)
    app.add_route('/path', resource)

    client = testing.TestClient(app)
    response = client.simulate_get(path='/path', headers=headers)

    assert response.status == falcon.HTTP_OK

    req = resource.captured_req
    assert req.context['oas.user'] == user


def test_success_without_user(resource):
    spec_dict = {'paths': {'/path': {'get': {'security': [{'session': []}]}}}}
    app = create_app(spec_dict)
    app.add_route('/path', resource)

    client = testing.TestClient(app)
    response = client.simulate_get(
        path='/path', headers={'Cookie': str('session=1')}
    )

    assert response.status == falcon.HTTP_OK

    req = resource.captured_req
    assert 'oas.user' not in req.context


@pytest.mark.parametrize(
    'headers,security',
    [
        ({'Cookie': str('')}, [{'session': []}]),
        ({'Cookie': str('session=none')}, [{'session': []}]),
        ({'Cookie': str('session=0')}, [{'session': []}]),
        (
            {'Cookie': str('session=0'), 'X-API-Key': str('user')},
            [{'session': [], 'api_key': []}],
        ),
        (
            {'Cookie': str('session=user'), 'X-API-Key': str('0')},
            [{'session': [], 'api_key': []}],
        ),
    ],
)
def test_forbidden(headers, security, resource):
    spec_dict = {'paths': {'/path': {'get': {'security': security}}}}
    app = create_app(spec_dict)
    app.add_route('/path', resource)

    client = testing.TestClient(app)
    response = client.simulate_get(path='/path', headers=headers)

    assert response.status == falcon.HTTP_FORBIDDEN
    assert resource.called is False


@pytest.mark.parametrize('key', ['http', 'oauth2', 'openIdConnect'])
def test_unsupported_type(key, resource):
    spec_dict = {'paths': {'/path': {'get': {'security': [{key: []}]}}}}
    app = create_app(spec_dict)
    app.add_route('/path', resource)

    client = testing.TestClient(app)
    client.simulate_get(path='/path')

    req = resource.captured_req
    assert 'oas.user' not in req.context


def test_without_user_loader(resource):
    spec_dict = {
        'paths': {
            '/path': {
                'get': {'security': [{'scheme_without_user_loader': []}]}
            }
        }
    }
    app = create_app(spec_dict)
    app.add_route('/path', resource)

    client = testing.TestClient(app)
    client.simulate_get(path='/path')

    req = resource.captured_req
    assert 'oas.user' not in req.context


def test_get_security_schemes():
    spec_dict = yaml_load_dedent(
        """\
        components:
          securitySchemes:
            session:
              type: apiKey
              name: session
              in: cookie
              {}: middlewares.test_security.session_user_loader
        """.format(
            FALCON_OAS_IMPLEMENTOR
        )
    )
    spec = create_spec_from_dict(spec_dict)

    result = get_security_schemes(spec, base_module='tests')
    assert result == {
        'session': (
            spec_dict['components']['securitySchemes']['session'],
            session_user_loader,
        )
    }


def test_get_security_schemes_none():
    spec = create_spec_from_dict({})

    assert get_security_schemes(spec) is None


def test_get_security_schemes_without_user_loader():
    spec_dict = yaml_load_dedent(
        """\
        components:
          securitySchemes:
            session:
              type: apiKey
              name: session
              in: cookie
        """
    )
    spec = create_spec_from_dict(spec_dict)

    assert get_security_schemes(spec) == {}
