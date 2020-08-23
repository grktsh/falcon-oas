# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
import pytest
from falcon import testing

from falcon_oas import extensions
from falcon_oas.factories import OAS


user = object()


def session_cookie_loader(value, scopes, req):
    return value and user


class PetCollection(object):
    def on_get(self, req, resp):
        pass

    def on_post(self, req, resp):
        resp.status = falcon.HTTP_CREATED


class PetItem(object):
    def on_get(self, req, resp, pet_id):
        resp.media = {'id': pet_id}

    def on_patch(self, req, resp, pet_id):
        resp.media = {'id': pet_id}

    def on_delete(self, req, resp, pet_id):
        resp.status = falcon.HTTP_NO_CONTENT


@pytest.fixture
def spec_dict(petstore_dict):
    path_item = petstore_dict['paths']['/v1/pets']
    path_item[extensions.IMPLEMENTATION] = 'test_factories.PetCollection'

    path_item = petstore_dict['paths']['/v1/pets/{pet_id}']
    path_item[extensions.IMPLEMENTATION] = 'test_factories.PetItem'

    return petstore_dict


@pytest.fixture
def spec_dict_with_security_loader(spec_dict):
    access_control = 'test_factories.session_cookie_loader'
    security_scheme = spec_dict['components']['securitySchemes']['session']
    security_scheme[extensions.IMPLEMENTATION] = access_control

    return spec_dict


def test_oas_default(spec_dict_with_security_loader):
    api = OAS(spec_dict_with_security_loader, base_module='tests').create_api()

    assert api.req_options.auto_parse_qs_csv is False

    client = testing.TestClient(api)

    # http error
    response = client.simulate_get(path='/')
    assert response.status == falcon.HTTP_NOT_FOUND
    assert response.headers['Content-Type'] == 'application/problem+json'

    # undocumented media type
    response = client.simulate_post(
        path='/api/v1/pets', headers={'Content-Type': str('text/plain')}
    )
    assert response.status == falcon.HTTP_BAD_REQUEST
    assert response.headers['Content-Type'] == 'application/problem+json'

    # security error
    response = client.simulate_delete(path='/api/v1/pets/42')
    assert response.status == falcon.HTTP_FORBIDDEN
    assert response.headers['Content-Type'] == 'application/problem+json'

    response = client.simulate_delete(
        path='/api/v1/pets/42', headers={'Cookie': str('session=1')}
    )
    assert response.status == falcon.HTTP_NO_CONTENT

    # unmarshal error
    response = client.simulate_get(path='/api/v1/pets/xxx')
    assert response.status == falcon.HTTP_BAD_REQUEST
    assert response.headers['Content-Type'] == 'application/problem+json'
    assert response.json['title'] == 'Unmarshal Error'

    response = client.simulate_get(path='/api/v1/pets/42')
    assert response.status == falcon.HTTP_OK
    assert response.json == {'id': 42}


def test_oas_disable_problems(spec_dict_with_security_loader):
    api = OAS(
        spec_dict_with_security_loader, base_module='tests', problems=False
    ).create_api()
    client = testing.TestClient(api)

    response = client.simulate_get(path='/')
    assert response.status == falcon.HTTP_NOT_FOUND
    assert response.headers['Content-Type'] == falcon.MEDIA_JSON

    response = client.simulate_get(path='/api/v1/pets/xxx')
    assert response.status == falcon.HTTP_BAD_REQUEST
    assert response.headers['Content-Type'] == falcon.MEDIA_JSON


def test_oas_without_middleware(spec_dict_with_security_loader):
    api = OAS(spec_dict_with_security_loader, base_module='tests').create_api(
        middleware=None
    )
    client = testing.TestClient(api)

    response = client.simulate_get(path='/api/v1/pets/42')
    assert response.status == falcon.HTTP_OK
    assert response.json == {'id': '42'}

    response = client.simulate_delete(path='/api/v1/pets/42')
    assert response.status == falcon.HTTP_NO_CONTENT


def test_oas_with_security_handlers(spec_dict):
    api = OAS(
        spec_dict,
        base_module='tests',
        security_handlers={'session': session_cookie_loader},
    ).create_api()
    client = testing.TestClient(api)

    # security error
    response = client.simulate_delete(path='/api/v1/pets/42')
    assert response.status == falcon.HTTP_FORBIDDEN
    assert response.headers['Content-Type'] == 'application/problem+json'

    response = client.simulate_delete(
        path='/api/v1/pets/42', headers={'Cookie': str('session=1')}
    )
    assert response.status == falcon.HTTP_NO_CONTENT
