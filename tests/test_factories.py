# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from falcon import testing

from falcon_oas.factories import create_api
from tests.helpers import yaml_load_dedent


class Resource(object):
    def on_get(self, req, resp):
        resp.media = {'x': 2}


class ElapsedMiddleware(object):
    def process_response(self, req, resp, resource, req_succeeded):
        resp.set_header('X-Elapsed', 100)


def api_key_loader(value):
    return bool(value)


def test_create_api():
    api = create_api(
        yaml_load_dedent(
            """\
            paths:
              /path:
                x-falcon-resource: test_factories:Resource
                get:
                  security: []
            components:
              securitySchemes:
                api_key:
                  type: apiKey
                  name: X-API-Key
                  in: header
                  x-user-loader: test_factories:api_key_loader
            """
        ),
        middlewares=[ElapsedMiddleware()],
        base_module='tests',
    )
    client = testing.TestClient(api)
    result = client.simulate_get('/path')
    assert result.json == {'x': 2}
    assert result.headers['X-Elapsed'] == '100'


def test_create_api_simple():
    api = create_api(
        yaml_load_dedent(
            """\
            paths:
              /path:
                x-falcon-resource: test_factories:Resource
                get:
                  security: []
            """
        ),
        base_module='tests',
    )
    client = testing.TestClient(api)
    result = client.simulate_get('/path')
    assert result.json == {'x': 2}
    assert 'X-Elapsed' not in result.headers
