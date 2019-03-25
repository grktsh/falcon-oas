# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import deque

import falcon
import pytest
from falcon import testing

import falcon_oas
from falcon_oas.middlewares.operation import OperationMiddleware
from falcon_oas.middlewares.request_unmarshal import RequestUnmarshalMiddleware
from falcon_oas.oas.exceptions import UnmarshalError
from falcon_oas.oas.schema.unmarshalers import SchemaUnmarshaler
from falcon_oas.oas.spec import create_spec_from_dict
from tests.helpers import yaml_load_dedent


def create_app(spec_dict):
    spec = create_spec_from_dict(spec_dict)
    app = falcon.API(
        middleware=[
            OperationMiddleware(spec),
            RequestUnmarshalMiddleware(SchemaUnmarshaler()),
        ],
        request_type=falcon_oas.Request,
    )
    return app


def test_undocumented_request(resource):
    app = create_app({'paths': {}})
    app.add_route('/undocumented', resource)

    client = testing.TestClient(app)
    response = client.simulate_get(path='/undocumented')

    assert response.status == falcon.HTTP_OK

    req = resource.captured_req
    assert req.context['oas'] is None


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
            - name: X-Version
              in: header
              schema:
                type: integer
            - name: c
              in: cookie
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
        headers={
            'Content-Type': str('application/json'),
            'X-Version': str('5'),
            'Cookie': str('c=7'),
        },
        body='"foo"',
    )

    req = resource.captured_req
    assert req.context['oas'].parameters == {
        'query': {'q': 3},
        'path': {'id': 2},
        'header': {'X-Version': 5},
        'cookie': {'c': 7},
    }
    assert req.context['oas'].request_body == 'foo'
    assert resource.captured_kwargs == {'id': 2}
    assert req.oas_query == {'q': 3}
    assert req.oas_header == {'X-Version': 5}
    assert req.oas_cookie == {'c': 7}
    assert req.oas_media == 'foo'


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
    assert req.context['oas'].parameters == {}
    assert req.context['oas'].request_body is None
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
    assert req.context['oas'].parameters == {}
    assert req.context['oas'].request_body == 'foo'


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
                required: true
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
            query_string=str('p1=a'),
            headers={'Content-Type': str('application/json')},
            body='3',
        )

    errors = exc_info.value.parameter_errors
    assert errors[0].message == "'a' is not of type 'integer'"
    assert errors[0].schema_path == deque(['parameters', 0, 'schema', 'type'])
    assert errors[1].message == "'p2' is a required in 'query' parameter"
    assert errors[1].schema_path == deque(['parameters', 1, 'required'])
    errors = exc_info.value.request_body_errors
    assert errors[0].message == "3 is not of type 'string'"
    assert errors[0].schema_path == deque(
        ['requestBody', 'content', 'application/json', 'schema', 'type']
    )

    assert resource.called is False
