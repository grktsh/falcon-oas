# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from falcon_oas.oas.exceptions import UndocumentedMediaType
from falcon_oas.oas.exceptions import UndocumentedRequest
from falcon_oas.oas.spec import create_spec_from_dict
from falcon_oas.oas.spec import get_base_path
from falcon_oas.oas.spec import get_security
from tests.helpers import yaml_load_dedent


def test_create_spec_from_dict():
    spec_dict = yaml_load_dedent(
        """\
        components:
          schemas:
            Foo:
              type: object
              properties:
                x:
                  type: integer
            Bar:
              type: object
              properties:
                foo:
                  $ref: '#/components/schemas/Foo'
        """
    )
    spec = create_spec_from_dict(spec_dict)

    bar_dict = spec.spec_dict['components']['schemas']['Bar']
    assert bar_dict['properties']['foo'] == yaml_load_dedent(
        """\
        type: object
        properties:
          x:
            type: integer
        """
    )


def test_spec_get_operation_parameters():
    spec = create_spec_from_dict(
        yaml_load_dedent(
            """\
            paths:
              /path:
                get:
                  parameters:
                  - name: param1
                    in: query
                  - name: param2
                    in: path
                parameters:
                - name: param1
                  in: query
                  required: true
                - name: param3
                  in: cookie
            """
        )
    )

    operation = spec.get_operation('/path', 'get', None)
    assert operation['parameters'] == [
        {'name': 'param1', 'in': 'query'},
        {'name': 'param2', 'in': 'path'},
        {'name': 'param3', 'in': 'cookie'},
    ]
    assert 'requestBody' not in operation


def test_spec_get_operation_parameters_deref():
    spec = create_spec_from_dict(
        yaml_load_dedent(
            """\
            paths:
              /path:
                get:
                  parameters:
                  - $ref: '#components/parameters/test_param'
            components:
              parameters:
                test_param:
                  name: param1
                  in: query
                  schema:
                    $ref: '#components/schemas/test_schema'
              schemas:
                test_schema:
                  type: string
            """
        )
    )

    operation = spec.get_operation('/path', 'get', None)
    assert operation['parameters'] == [
        {'name': 'param1', 'in': 'query', 'schema': {'type': 'string'}}
    ]


def test_spec_get_operation_request_body():
    spec = create_spec_from_dict(
        yaml_load_dedent(
            """\
            paths:
              /path:
                get:
                  requestBody:
                    content:
                      application/json: {}
            """
        )
    )

    operation = spec.get_operation('/path', 'get', 'application/json')
    assert operation['parameters'] == []
    assert operation['requestBody'] == {'content': {'application/json': {}}}


def test_spec_get_operation_request_body_undocumented_media_type():
    spec = create_spec_from_dict(
        yaml_load_dedent(
            """\
            paths:
              /path:
                get:
                  requestBody:
                    content:
                      application/json: {}
            """
        )
    )

    with pytest.raises(UndocumentedMediaType):
        spec.get_operation('/path', 'get', 'text/plain')


def test_spec_get_operation_request_body_deref():
    spec = create_spec_from_dict(
        yaml_load_dedent(
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
    )
    operation = spec.get_operation('/path', 'post', 'application/json')
    assert operation['requestBody'] == {
        'content': {'application/json': {'schema': {'type': 'string'}}}
    }


def test_spec_get_operation_unknown_base_path():
    spec = create_spec_from_dict({'servers': [{'url': '/api'}], 'paths': {}})
    with pytest.raises(UndocumentedRequest):
        spec.get_operation('/path', 'get', None)


def test_spec_get_operation_undocumented_operation():
    spec = create_spec_from_dict({})
    with pytest.raises(UndocumentedRequest):
        spec.get_operation('/path', 'get', None)


def test_spec_get_operation_security():
    spec = create_spec_from_dict(
        yaml_load_dedent(
            """\
            paths:
              /path:
                get:
                  security:
                  - test_scheme:
                    - test_scope
            """
        )
    )
    operation = spec.get_operation('/path', 'get', None)
    assert operation['security'] == [{'test_scheme': ['test_scope']}]


def test_spec_get_security_schemes():
    spec = create_spec_from_dict(
        yaml_load_dedent(
            """\
            components:
              securitySchemes:
                api_key:
                  $ref: '#components/schemas/api_key'
              schemas:
                api_key:
                  type: apiKey
                  name: X-API-Key
                  in: header
            """
        )
    )

    assert spec.get_security_schemes() == {
        'api_key': {'type': 'apiKey', 'name': 'X-API-Key', 'in': 'header'}
    }


def test_spec_get_security_schemes_none():
    spec = create_spec_from_dict({})

    assert spec.get_security_schemes() is None


@pytest.mark.parametrize(
    'spec_dict,expected',
    [
        ({}, ''),
        ({'servers': []}, ''),
        ({'servers': [{'url': '/'}]}, ''),
        ({'servers': [{'url': '/path/'}]}, '/path'),
        ({'servers': [{'url': '/path'}]}, '/path'),
        ({'servers': [{'url': 'http://example.org'}]}, ''),
        ({'servers': [{'url': 'http://example.org/'}]}, ''),
        ({'servers': [{'url': 'http://example.org/path'}]}, '/path'),
        ({'servers': [{'url': 'http://example.org/path/'}]}, '/path'),
        ({'servers': [{'url': '/path1'}, {'url': '/path2'}]}, '/path1'),
    ],
)
def test_base_path(spec_dict, expected):
    assert get_base_path(spec_dict) == expected


@pytest.mark.parametrize(
    'spec_dict,base_security,expected',
    [
        ({}, None, None),
        ({}, [], []),
        ({'security': []}, None, []),
        ({'security': []}, [{'test_scheme': []}], []),
    ],
)
def test_security(spec_dict, base_security, expected):
    assert get_security(spec_dict, base_security=base_security) == expected
