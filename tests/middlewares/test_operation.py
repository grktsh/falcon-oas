# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
import pytest
from falcon import testing

from falcon_oas.middlewares.operation import _RequestAdapter
from falcon_oas.middlewares.operation import OperationMiddleware
from falcon_oas.oas.spec import create_spec_from_dict
from tests.helpers import yaml_load_dedent


def create_app(spec_dict):
    spec = create_spec_from_dict(spec_dict)
    app = falcon.API(middleware=[OperationMiddleware(spec)])
    return app


@pytest.fixture
def req():
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
    req = falcon.Request(env)
    req.uri_template = '/users/{id}'
    return _RequestAdapter(req, {'id': '42'})


def test_request_adapter(req):
    assert req.uri_template == '/users/{id}'
    assert req.method == 'get'
    assert req.parameters['query'] == {'page': '1'}
    assert req.parameters['header']['x-api-key'] == 'secret-key'
    assert req.parameters['path'] == {'id': '42'}
    assert req.parameters['cookie'] == {'session': 'secret'}
    assert req.media_type == 'application/json'
    assert req.get_media() == {'foo': 'bar'}

    pytest.raises(KeyError, lambda: req.parameters['header']['unknown'])


def test_undocumented_media_type(resource):
    spec_dict = yaml_load_dedent(
        """\
        paths:
          /path:
            get:
              requestBody:
                content:
                  application/json: {}
        """
    )
    app = create_app(spec_dict)
    app.add_route('/path', resource)

    client = testing.TestClient(app)
    response = client.simulate_get(
        path='/path', headers={'Content-Type': str('text/plain')}
    )

    assert response.status == falcon.HTTP_BAD_REQUEST


def test_undocumented_request(resource):
    app = create_app({'paths': {}})
    app.add_route('/undocumented', resource)

    client = testing.TestClient(app)
    response = client.simulate_get(path='/undocumented')

    assert response.status == falcon.HTTP_OK

    req = resource.captured_req
    assert req.context['oas.operation'] is None


def test_documented_request(resource):
    app = create_app({'paths': {'/path/{id}': {'post': {}}}})
    app.add_route('/path/{id}', resource)

    client = testing.TestClient(app)
    client.simulate_post(
        path='/path/2',
        query_string=str('q=3&r=5&r=7'),
        headers={
            'Content-Type': str('application/json; charset=UTF-8'),
            'Cookie': str('x=5'),
            'X-Key': str('key'),
        },
        body='"foo"',
    )

    req = resource.captured_req
    assert req.context['oas.operation'] is not None
    assert req.context['oas.request'].parameters['query'] == {
        'q': '3',
        'r': ['5', '7'],
    }
    assert req.context['oas.request'].parameters['header']['X-Key'] == 'key'
    assert req.context['oas.request'].parameters['path'] == {'id': '2'}
    assert req.context['oas.request'].parameters['cookie'] == {'x': '5'}
    assert req.context['oas.request'].media_type == 'application/json'
    assert req.context['oas.request'].get_media() == 'foo'
