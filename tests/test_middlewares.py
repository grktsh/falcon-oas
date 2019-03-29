# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
import pytest
from falcon import testing

import falcon_oas
from falcon_oas import extensions
from falcon_oas.middlewares import _get_security_schemes
from falcon_oas.middlewares import _RequestAdapter
from falcon_oas.oas.exceptions import SecurityError
from falcon_oas.oas.exceptions import UndocumentedMediaType
from falcon_oas.oas.exceptions import UnmarshalError
from falcon_oas.oas.spec import create_spec_from_dict


user = object()


def session_cookie_loader(value, scopes, request):
    return value and user


@pytest.fixture
def petstore_dict_with_implementation(petstore_dict):
    name = 'tests.test_middlewares.session_cookie_loader'
    security_scheme = petstore_dict['components']['securitySchemes']['session']
    security_scheme[extensions.IMPLEMENTATION] = name
    return petstore_dict


@pytest.fixture
def resource():
    class Resource(testing.SimpleTestResource):
        on_patch = testing.SimpleTestResource.on_get

    return Resource()


def create_app(spec_dict):
    spec = create_spec_from_dict(spec_dict)
    app = falcon.API(
        middleware=[falcon_oas.Middleware(spec)],
        request_type=falcon_oas.Request,
    )
    return app


def test_request_adapter(mocker):
    env = testing.create_environ(
        query_string='page=1',
        headers={
            'X-API-Key': 'secret-key',
            'Cookie': str('session=secret'),
            'Content-Type': 'application/json',
        },
        body='{"foo": "bar"}',
        method='GET',
    )
    falcon_req = falcon.Request(env)
    falcon_req.uri_template = '/users/{id}'
    falcon_req.context['x'] = 42
    req = _RequestAdapter(falcon_req, {'id': '42'})

    assert req.uri_template == '/users/{id}'
    assert req.method == 'get'
    assert req.context['x'] == 42
    assert req.path == {'id': '42'}
    assert req.query == {'page': '1'}
    assert req.header['x-api-key'] == 'secret-key'
    assert req.cookie == {'session': 'secret'}
    assert req.content_length == len('{"foo": "bar"}')
    assert req.media_type == 'application/json'
    assert req.media == {'foo': 'bar'}

    with pytest.raises(KeyError):
        req.header['unknown']

    with pytest.raises(falcon.HTTPBadRequest):
        falcon_req = mocker.MagicMock()
        type(falcon_req).media = mocker.PropertyMock(side_effect=ValueError)
        req = _RequestAdapter(falcon_req, {})
        req.media


def test_undocumented_media_type(resource, petstore_dict):
    app = create_app(petstore_dict)
    app.add_route('/api/v1/pets', resource)

    client = testing.TestClient(app)

    with pytest.raises(UndocumentedMediaType):
        client.simulate_post(
            path='/api/v1/pets',
            headers={'Content-Type': str('text/plain')},
            body='{}',
        )

    assert resource.called is False


def test_undocumented_request(resource):
    app = create_app({'paths': {}})
    app.add_route('/undocumented', resource)

    client = testing.TestClient(app)
    response = client.simulate_get(path='/undocumented')

    assert response.status == falcon.HTTP_OK
    assert resource.called

    req = resource.captured_req
    assert 'oas' not in req.context


def test_security(resource, petstore_dict_with_implementation):
    app = create_app(petstore_dict_with_implementation)
    app.add_route('/api/v1/pets', resource)

    client = testing.TestClient(app)

    response = client.simulate_post(
        path='/api/v1/pets',
        headers={'Cookie': str('session=1')},
        json={'name': 'momo'},
    )

    assert response.status == falcon.HTTP_OK
    assert resource.called

    req = resource.captured_req
    assert req.context['oas'].user is user
    assert req.oas_user is user


def test_security_error(resource, petstore_dict_with_implementation):
    app = create_app(petstore_dict_with_implementation)
    app.add_route('/api/v1/pets', resource)

    client = testing.TestClient(app)

    with pytest.raises(SecurityError):
        client.simulate_post(path='/api/v1/pets', json={'name': 'momo'})

    assert resource.called is False


def test_unmarshal_request(resource, petstore_dict):
    app = create_app(petstore_dict)
    app.add_route('/api/v1/pets/{pet_id}', resource)

    client = testing.TestClient(app)

    response = client.simulate_patch(
        path='/api/v1/pets/42',
        query_string=str('page=1'),
        headers={'X-API-Version': str('v2'), 'Cookie': str('tracking=xxx')},
        json={'name': 'momo'},
    )

    assert response.status == falcon.HTTP_OK
    assert resource.called

    req = resource.captured_req
    assert req.context['oas'].parameters['path'] == {'pet_id': 42}
    assert req.context['oas'].parameters['query'] == {'page': 1}
    assert req.context['oas'].parameters['header'] == {'X-API-Version': 'v2'}
    assert req.context['oas'].parameters['cookie'] == {'tracking': 'xxx'}
    assert req.context['oas'].request_body == {'name': 'momo'}

    kwargs = resource.captured_kwargs
    assert kwargs['pet_id'] == 42

    assert req.oas_query == {'page': 1}
    assert req.oas_header == {'X-API-Version': 'v2'}
    assert req.oas_cookie == {'tracking': 'xxx'}
    assert req.oas_media == {'name': 'momo'}


def test_unmarshal_request_error(resource, petstore_dict):
    app = create_app(petstore_dict)
    app.add_route('/api/v1/pets/{pet_id}', resource)

    client = testing.TestClient(app)

    with pytest.raises(UnmarshalError):
        client.simulate_get(path='/api/v1/pets/xxx')

    assert resource.called is False


def test_get_security_schemes(petstore_dict_with_implementation):
    spec_dict = petstore_dict_with_implementation
    security_scheme = spec_dict['components']['securitySchemes']['session']

    spec = create_spec_from_dict(spec_dict)

    result = _get_security_schemes(spec)
    assert result == {'session': (security_scheme, session_cookie_loader)}


def test_get_security_schemes_none():
    spec = create_spec_from_dict({})

    assert _get_security_schemes(spec) is None


def test_get_security_schemes_without_user_loader(petstore_dict):
    spec = create_spec_from_dict(petstore_dict)

    assert _get_security_schemes(spec) == {}
