# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
import pytest
from falcon import testing

from falcon_oas.extensions import FALCON_OAS_IMPLEMENTOR
from falcon_oas.factories import OAS
from falcon_oas.oas.exceptions import UnmarshalError
from tests.helpers import yaml_load_dedent


spec_dict = yaml_load_dedent(
    """\
    paths:
      /security:
        {0}: test_factories.SecurityResource
        get:
          security:
          - api_key: []
      /request-unmarshal/{{pet_id}}:
        {0}: test_factories.RequestUnmarshalResource
        get:
          security: []
          parameters:
          - name: pet_id
            in: path
            required: true
            schema:
              type: integer
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


class SecurityResource(object):
    def on_get(self, req, resp):
        pass


class RequestUnmarshalResource(object):
    def on_get(self, req, resp, pet_id):
        resp.media = {'pet_id': pet_id}


def api_key_loader(value, scopes, req):
    return value == 'secret'


def test_oas_default():
    api = OAS(spec_dict, base_module='tests').create_api()

    assert api.req_options.auto_parse_qs_csv is False

    client = testing.TestClient(api)

    response = client.simulate_get(path='/')
    assert response.status == falcon.HTTP_NOT_FOUND
    assert response.headers['Content-Type'] == 'application/problem+json'

    response = client.simulate_get(
        path='/security', headers={'X-API-Key': str('secret')}
    )
    assert response.status == falcon.HTTP_OK

    response = client.simulate_get(path='/security')
    assert response.status == falcon.HTTP_FORBIDDEN

    response = client.simulate_get(path='/request-unmarshal/42')
    assert response.status == falcon.HTTP_OK
    assert response.json == {'pet_id': 42}

    response = client.simulate_get(path='/request-unmarshal/xxx')
    assert response.status == falcon.HTTP_BAD_REQUEST
    assert response.headers['Content-Type'] == 'application/problem+json'
    assert response.json['title'] == 'Unmarshal Error'


def test_oas_disable_problems():
    api = OAS(spec_dict, base_module='tests', problems=False).create_api()
    client = testing.TestClient(api)

    response = client.simulate_get(path='/')

    assert response.status == falcon.HTTP_NOT_FOUND
    assert response.headers['Content-Type'] == falcon.MEDIA_JSON

    with pytest.raises(UnmarshalError):
        client.simulate_get(path='/request-unmarshal/xxx')


def test_oas_without_middlewares():
    api = OAS(spec_dict, base_module='tests').create_api(middleware=None)
    client = testing.TestClient(api)

    response = client.simulate_get(path='/request-unmarshal/42')
    assert response.status == falcon.HTTP_OK
    assert response.json == {'pet_id': '42'}

    response = client.simulate_get(path='/security')
    assert response.status == falcon.HTTP_OK
