# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from falcon_oas.oas.exceptions import UndocumentedMediaType
from falcon_oas.oas.spec import _get_base_path
from falcon_oas.oas.spec import _get_security
from falcon_oas.oas.spec import create_spec_from_dict


@pytest.fixture
def media_type():
    return 'application/json'


def test_create_spec_from_dict(petstore_dict):
    spec = create_spec_from_dict(petstore_dict)

    schemas = spec.spec_dict['components']['schemas']
    assert schemas['PetNew']['allOf'][0] == schemas['PetUpdate']


def test_spec_get_operation_parameters(petstore_dict, media_type):
    operation_dict = petstore_dict['paths']['/v1/pets/{pet_id}']['get']
    operation_dict['parameters'] = [
        {'name': 'page', 'in': 'query'},
        {'name': 'limit', 'in': 'query'},
        {'name': 'pet_id', 'in': 'query'},
        {'name': 'pet_id', 'in': 'path'},
    ]
    spec = create_spec_from_dict(petstore_dict)

    operation = spec.get_operation('/api/v1/pets/{pet_id}', 'get', media_type)
    assert operation['parameters'] == operation_dict['parameters']
    assert 'requestBody' not in operation


def test_spec_get_operation_request_body_and_security(
    petstore_dict, media_type
):
    spec = create_spec_from_dict(petstore_dict)
    schemas = spec.spec_dict['components']['schemas']

    operation = spec.get_operation('/api/v1/pets', 'post', media_type)
    assert operation['parameters'] == []
    assert operation['requestBody'] == {
        'content': {media_type: {'schema': schemas['PetNew']}},
        'required': True,
    }
    assert operation['security'] == [{'api_key': []}, {'session': []}]


def test_spec_get_operation_request_body_undocumented_media_type(
    petstore_dict
):
    spec = create_spec_from_dict(petstore_dict)

    with pytest.raises(UndocumentedMediaType):
        spec.get_operation('/api/v1/pets', 'post', 'text/plain')


def test_spec_get_operation_unknown_base_path():
    spec = create_spec_from_dict({'servers': [{'url': '/api'}], 'paths': {}})
    assert spec.get_operation('/path', 'get', None) is None


def test_spec_get_operation_undocumented_operation():
    spec = create_spec_from_dict({})
    assert spec.get_operation('/path', 'get', None) is None


def test_spec_get_security_schemes(petstore_dict):
    spec = create_spec_from_dict(petstore_dict)
    components = spec.spec_dict['components']

    assert spec.get_security_schemes() == components['securitySchemes']


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
    assert _get_base_path(spec_dict) == expected


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
    assert _get_security(spec_dict, base_security=base_security) == expected
