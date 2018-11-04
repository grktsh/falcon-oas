# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
import pytest
from falcon import testing

import falcon_oas
from falcon_oas.factories import create_request_unmarshaler
from falcon_oas.factories import create_spec_from_dict
from falcon_oas.oas.exceptions import UnmarshalError
from tests.helpers import yaml_load_dedent


@pytest.fixture
def resource():
    return None


def test_undocumented_request(resource):
    req = falcon.Request(testing.create_environ())
    req.uri_template = '/'
    resp = falcon.Response()
    params = {}

    spec = create_spec_from_dict({'paths': {}})
    unmarshaler = create_request_unmarshaler(spec)
    unmarshaler.process_resource(req, resp, resource, params)

    assert req.context == {}


def test_success():
    spec_dict = yaml_load_dedent(
        """\
        paths:
          /resources/{id}:
            patch:
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

    req = falcon_oas.Request(
        testing.create_environ(
            path='/resources/2',
            method='PATCH',
            body='"foo"',
            query_string='q=3',
            headers={'Content-Type': 'application/json'},
        )
    )
    req.uri_template = '/resources/{id}'
    resp = falcon.Response()
    params = {'id': '2'}

    spec = create_spec_from_dict(spec_dict)
    unmarshaler = create_request_unmarshaler(spec)
    unmarshaler.process_resource(req, resp, resource, params)

    assert req.context['oas.parameters'] == {
        'query': {'q': 3},
        'path': {'id': 2},
    }
    assert req.context['oas.request_body'] == 'foo'
    assert params == {'id': 2}
    assert req.oas_query == {'q': 3}
    assert req.oas_media == 'foo'


def test_success_without_request_body():
    spec_dict = yaml_load_dedent(
        """\
        paths:
          /resources:
            get: {}
        """
    )

    req = falcon.Request(
        testing.create_environ(
            path='/resources',
            method='GET',
            headers={'Content-Type': 'application/json'},
        )
    )
    req.uri_template = '/resources'
    resp = falcon.Response()
    params = {}

    spec = create_spec_from_dict(spec_dict)
    unmarshaler = create_request_unmarshaler(spec)
    unmarshaler.process_resource(req, resp, resource, params)

    assert req.context['oas.parameters'] == {}
    assert 'oas.request_body' not in req.context
    assert params == {}


def test_errors():
    spec_dict = yaml_load_dedent(
        """\
        paths:
          /resources:
            patch:
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

    req = falcon.Request(
        testing.create_environ(
            path='/resources',
            method='PATCH',
            query_string=str('p1=a&p2=b'),
            body='3',
            headers={'Content-Type': 'application/json'},
        )
    )
    req.uri_template = '/resources'
    resp = falcon.Response()
    params = {}

    spec = create_spec_from_dict(spec_dict)
    unmarshaler = create_request_unmarshaler(spec)
    with pytest.raises(UnmarshalError) as exc_info:
        unmarshaler.process_resource(req, resp, resource, params)

    errors = exc_info.value.parameters_error.errors
    assert errors[0].errors[0].message == "'a' is not of type 'integer'"
    assert errors[1].errors[0].message == "'b' is not of type 'integer'"
    errors = exc_info.value.request_body_error.errors
    assert errors[0].message == "3 is not of type 'string'"


def test_missing_media_type():
    spec_dict = yaml_load_dedent(
        """\
        paths:
          /resources:
            patch:
              requestBody:
                content:
                  application/json:
                    schema:
                      type: integer
        """
    )

    req = falcon.Request(
        testing.create_environ(path='/resources', method='PATCH', body='123')
    )
    req.uri_template = '/resources'
    resp = falcon.Response()
    params = {}

    spec = create_spec_from_dict(spec_dict)
    unmarshaler = create_request_unmarshaler(spec)
    with pytest.raises(UnmarshalError) as exc_info:
        unmarshaler.process_resource(req, resp, resource, params)

    assert exc_info.value.parameters_error is None
    errors = exc_info.value.request_body_error.errors
    assert errors[0].path is None
    assert errors[0].validator == 'required'
    assert errors[0].message == 'media type is required'
