# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
import pytest
from falcon import testing

from falcon_oas.factories import create_request_unmarshal_middleware
from falcon_oas.middlewares.operation import OperationMiddleware
from falcon_oas.oas.exceptions import UnmarshalError
from falcon_oas.oas.spec import create_spec_from_dict
from tests.helpers import yaml_load_dedent


def create_app(spec_dict):
    spec = create_spec_from_dict(spec_dict)
    app = falcon.API(
        middleware=[
            OperationMiddleware(spec),
            create_request_unmarshal_middleware(spec),
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
    assert 'oas.parameters' not in req.context
    assert 'oas.request_body' not in req.context


def test_success(resource):
    spec_dict = yaml_load_dedent(
        """\
        paths:
          /path/{id}:
            post:
              requestBody:
                content:
                  application/json:
                    schema:
                      type: string
            parameters:
            - name: id
              in: path
              schema:
                type: integer
            - name: q
              in: query
              schema:
                type: integer
        """
    )
    app = create_app(spec_dict)
    app.add_route('/path/{id}', resource)

    client = testing.TestClient(app)
    client.simulate_post(
        path='/path/2',
        query_string=str('q=3'),
        headers={'Content-Type': str('application/json')},
        body='"foo"',
    )

    req = resource.captured_req
    assert req.context['oas.parameters'] == {
        'query': {'q': 3},
        'path': {'id': 2},
    }
    assert req.context['oas.request_body'] == 'foo'
    assert resource.captured_kwargs == {'id': 2}


def test_success_without_request_body(resource):
    spec_dict = yaml_load_dedent(
        """\
        paths:
          /path:
            get: {}
        """
    )
    app = create_app(spec_dict)
    app.add_route('/path', resource)

    client = testing.TestClient(app)
    client.simulate_get(
        path='/path', headers={'Content-Type': str('application/json')}
    )

    req = resource.captured_req
    assert req.context['oas.parameters'] == {}
    assert 'oas.request_body' not in req.context
    assert resource.captured_kwargs == {}


def test_success_request_body_with_ref(resource):
    spec_dict = yaml_load_dedent(
        """\
        paths:
          /path:
            post:
              requestBody:
                $ref: '#components/requestBodies/test_body'
        components:
          requestBodies:
            test_body:
              content:
                application/json:
                  schema:
                    $ref: '#components/schemas/test_schema'
          schemas:
            test_schema:
              type: string
        """
    )
    app = create_app(spec_dict)
    app.add_route('/path', resource)

    client = testing.TestClient(app)
    client.simulate_post(
        path='/path',
        headers={'Content-Type': str('application/json')},
        body='"foo"',
    )

    req = resource.captured_req
    assert req.context['oas.parameters'] == {}
    assert req.context['oas.request_body'] == 'foo'


def test_errors(resource):
    spec_dict = yaml_load_dedent(
        """\
        paths:
          /path:
            post:
              parameters:
              - name: p1
                in: query
                schema:
                  type: integer
              - name: p2
                in: query
                schema:
                  type: integer
              requestBody:
                content:
                  application/json:
                    schema:
                      type: string
        """
    )
    app = create_app(spec_dict)
    app.add_route('/path', resource)

    client = testing.TestClient(app)
    with pytest.raises(UnmarshalError) as exc_info:
        client.simulate_post(
            path='/path',
            query_string=str('p1=a&p2=b'),
            headers={'Content-Type': str('application/json')},
            body='3',
        )

    errors = exc_info.value.parameters_error.errors
    assert errors[0].errors[0].message == "'a' is not of type 'integer'"
    assert errors[1].errors[0].message == "'b' is not of type 'integer'"
    errors = exc_info.value.request_body_error.errors
    assert errors[0].message == "3 is not of type 'string'"

    assert resource.called is False
