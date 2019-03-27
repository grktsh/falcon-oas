# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

import pytest

from falcon_oas.oas.exceptions import UnmarshalError
from falcon_oas.oas.request.unmarshalers import unmarshal_request
from falcon_oas.oas.schema.unmarshalers import SchemaUnmarshaler


@pytest.fixture
def schema_unmarshaler():
    return SchemaUnmarshaler()


@pytest.fixture
def media_type():
    return 'application/json'


def test_unmarshal_request(mocker, schema_unmarshaler, media_type):
    request = mocker.MagicMock(
        query={'p': '42'}, media='2020-01-02', media_type=media_type
    )
    operation = {
        'parameters': [
            {'name': 'p', 'in': 'query', 'schema': {'type': 'integer'}}
        ],
        'requestBody': {
            'content': {
                media_type: {'schema': {'type': 'string', 'format': 'date'}}
            }
        },
    }
    parameters, request_body = unmarshal_request(
        schema_unmarshaler, request, operation
    )
    assert parameters == {'query': {'p': 42}}
    assert request_body == datetime.date(2020, 1, 2)


def test_unmarshal_request_without_request_body(
    mocker, schema_unmarshaler, media_type
):
    request = mocker.MagicMock(
        query={'p': '42'}, media='2020-01-02', media_type=media_type
    )
    operation = {
        'parameters': [
            {'name': 'p', 'in': 'query', 'schema': {'type': 'integer'}}
        ]
    }
    parameters, request_body = unmarshal_request(
        schema_unmarshaler, request, operation
    )
    assert parameters == {'query': {'p': 42}}
    assert request_body is None


def test_unmarshal_request_error(mocker, schema_unmarshaler, media_type):
    request = mocker.MagicMock(
        query={'p': '!'}, media='2020/01/02', media_type=media_type
    )
    operation = {
        'parameters': [
            {'name': 'p', 'in': 'query', 'schema': {'type': 'integer'}}
        ],
        'requestBody': {
            'content': {
                media_type: {'schema': {'type': 'string', 'format': 'date'}}
            }
        },
    }
    with pytest.raises(UnmarshalError) as exc_info:
        unmarshal_request(schema_unmarshaler, request, operation)

    parameter_errors = exc_info.value.parameter_errors
    assert len(parameter_errors) == 1
    assert parameter_errors[0].schema_path[0] == 'parameters'
    request_body_errors = exc_info.value.request_body_errors
    assert len(request_body_errors) == 1
    assert request_body_errors[0].schema_path[0] == 'requestBody'
