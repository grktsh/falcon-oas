# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from collections import deque

import falcon
import jsonschema
import pytest

from falcon_oas.oas.request_body import RequestBodyUnmarshaler
from falcon_oas.oas.schema.unmarshalers import SchemaUnmarshaler


@pytest.fixture
def unmarshal():
    return RequestBodyUnmarshaler(SchemaUnmarshaler()).unmarshal


@pytest.fixture
def media_type():
    return 'application/json'


def test_missing_required(mocker, unmarshal):
    request_body = mocker.MagicMock(content_length=0)
    request_body_spec_dict = {'content': {}, 'required': True}

    _, errors = unmarshal(request_body, request_body_spec_dict)

    assert len(errors) == 1
    error = errors[0]
    assert isinstance(error, jsonschema.ValidationError)
    assert error.message == 'Request body is required'
    assert error.validator == 'required'
    assert error.validator_value is True
    assert error.schema == request_body_spec_dict
    assert error.schema_path == deque(['required'])
    assert error.path == deque([])


def test_missing_optional(mocker, unmarshal):
    request_body = mocker.MagicMock(content_length=0)
    request_body_spec_dict = {'content': {}}

    result = unmarshal(request_body, request_body_spec_dict)

    assert result == (None, None)


def test_media_error(mocker, unmarshal):
    request_body = mocker.MagicMock()
    type(request_body).media = mocker.PropertyMock(
        side_effect=falcon.HTTPBadRequest
    )
    request_body_spec_dict = {'content': {}}

    with pytest.raises(falcon.HTTPBadRequest):
        unmarshal(request_body, request_body_spec_dict)


def test_undocumented_media_type_schema(mocker, unmarshal, media_type):
    request_body = mocker.MagicMock(media='foo', media_type=media_type)
    request_body_spec_dict = {'content': {media_type: {}}}

    result = unmarshal(request_body, request_body_spec_dict)

    assert result == ('foo', None)


def test_unmarshal_success(mocker, unmarshal, media_type):
    request_body = mocker.MagicMock(media='2018-01-02', media_type=media_type)
    request_body_spec_dict = {
        'content': {
            media_type: {'schema': {'type': 'string', 'format': 'date'}}
        }
    }
    result = unmarshal(request_body, request_body_spec_dict)

    assert result == (datetime.date(2018, 1, 2), None)


def test_unmarshal_error(mocker, unmarshal, media_type):
    request_body = mocker.MagicMock(
        media=str('2018/01/02'), media_type=media_type
    )
    request_body_spec_dict = {
        'content': {
            media_type: {'schema': {'type': 'string', 'format': str('date')}}
        }
    }
    _, errors = unmarshal(request_body, request_body_spec_dict)

    assert len(errors) == 1
    error = errors[0]
    assert isinstance(error, jsonschema.ValidationError)
    assert error.message == "'2018/01/02' is not a 'date'"
    assert error.validator == 'format'
    assert error.validator_value == 'date'
    assert error.schema == {'type': 'string', 'format': str('date')}
    assert error.schema_path == deque(
        ['content', media_type, 'schema', 'format']
    )
    assert error.path == deque([])
