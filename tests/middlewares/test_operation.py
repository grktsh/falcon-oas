# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
from falcon import testing

from falcon_oas.middlewares.operation import OperationMiddleware
from falcon_oas.oas.spec import create_spec_from_dict
from tests.helpers import yaml_load_dedent


def create_app(spec_dict):
    spec = create_spec_from_dict(spec_dict)
    app = falcon.API(middleware=[OperationMiddleware(spec)])
    return app


def test_undocumented_request(resource):
    app = create_app({'paths': {}})
    app.add_route('/undocumented', resource)

    client = testing.TestClient(app)
    client.simulate_get(path='/undocumented')

    req = resource.captured_req
    assert req.context['oas._operation'] is None


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
    client.simulate_get(
        path='/path', headers={'Content-Type': str('text/plain')}
    )

    req = resource.captured_req
    assert req.context['oas._operation'] is None


def test_documented_request(resource):
    app = create_app({'paths': {'/path/{id}': {'post': {}}}})
    app.add_route('/path/{id}', resource)

    client = testing.TestClient(app)
    client.simulate_post(
        path='/path/2',
        query_string=str('q=3'),
        headers={
            'Content-Type': str('application/json; charset=UTF-8'),
            'Cookie': str('x=5'),
            'X-Key': str('key'),
        },
        body='"foo"',
    )

    req = resource.captured_req
    assert req.context['oas._operation'] is not None
    assert req.context['oas._request'].parameters['query'] == {'q': '3'}
    assert req.context['oas._request'].parameters['header']['X-Key'] == 'key'
    assert req.context['oas._request'].parameters['path'] == {'id': '2'}
    assert req.context['oas._request'].parameters['cookie'] == {'x': '5'}
    assert req.context['oas._request'].media_type == 'application/json'
    assert req.context['oas._request'].get_media() == 'foo'
