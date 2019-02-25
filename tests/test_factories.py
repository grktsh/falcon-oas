# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from distutils.util import strtobool

import falcon
import pytest
from falcon import testing

from falcon_oas.extensions import FALCON_OAS_IMPLEMENTOR
from falcon_oas.factories import create_api
from tests.helpers import yaml_load_dedent


spec_dict = yaml_load_dedent(
    """\
    paths:
      /path:
        {0}: test_factories.Resource
        post:
          security:
          - api_key: []
        get:
          security: []
    components:
      securitySchemes:
        api_key:
          type: apiKey
          name: X-API-Key
          in: header
          {0}: test_factories.api_key_loader
    """.format(
        FALCON_OAS_IMPLEMENTOR
    )
)


class Resource(object):
    def on_post(self, req, resp):
        resp.media = {'x': 'post'}

    def on_get(self, req, resp):
        resp.media = {'x': 'get'}


class ElapsedMiddleware(object):
    def process_response(self, req, resp, resource, req_succeeded):
        resp.set_header('X-Elapsed', 100)


def api_key_loader(value, scopes, req):
    return value and strtobool(value)


@pytest.mark.parametrize(
    'method,headers,status',
    [
        ('POST', None, falcon.HTTP_FORBIDDEN),
        ('POST', {'X-API-Key': str('0')}, falcon.HTTP_FORBIDDEN),
        ('POST', {'X-API-Key': str('1')}, falcon.HTTP_OK),
        ('GET', None, falcon.HTTP_OK),
        ('GET', {'X-API-Key': str('0')}, falcon.HTTP_OK),
        ('GET', {'X-API-Key': str('1')}, falcon.HTTP_OK),
    ],
)
def test_create_api_default(method, headers, status):
    api = create_api(spec_dict, base_module='tests')
    client = testing.TestClient(api)
    response = client.simulate_request(
        str(method), path='/path', headers=headers
    )
    assert response.status == status


def test_create_api_with_middlewares():
    api = create_api(
        spec_dict, middlewares=[ElapsedMiddleware()], base_module='tests'
    )
    client = testing.TestClient(api)
    response = client.simulate_post(path='/path')

    assert response.status == falcon.HTTP_FORBIDDEN
    assert response.headers['X-Elapsed'] == '100'
