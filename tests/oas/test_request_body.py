# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

import pytest

from falcon_oas.oas.exceptions import MissingRequestBody
from falcon_oas.oas.exceptions import RequestBodyError
from falcon_oas.oas.request_body import RequestBodyUnmarshaler
from falcon_oas.oas.schema.unmarshalers import SchemaUnmarshaler
from falcon_oas.oas.spec import create_spec_from_dict


@pytest.fixture
def unmarshaler():
    spec = create_spec_from_dict({})
    unmarshaler = SchemaUnmarshaler(spec)
    return RequestBodyUnmarshaler(unmarshaler)


@pytest.fixture
def media_type():
    return 'application/json'


def test_missing_required(unmarshaler, media_type):
    def get_value():
        import json

        return json.loads('')

    request_body_spec_dict = {'content': {}, 'required': True}
    with pytest.raises(MissingRequestBody):
        unmarshaler.unmarshal(get_value, media_type, request_body_spec_dict)


def test_missing_optional(unmarshaler, media_type):
    def get_value():
        import json

        return json.loads('')

    request_body_spec_dict = {'content': {}}
    unmarshaled = unmarshaler.unmarshal(
        get_value, media_type, request_body_spec_dict
    )
    assert unmarshaled is None


def test_undocumented_media_type_schema(unmarshaler, media_type):
    def get_value():
        return 'foo'

    request_body_spec_dict = {'content': {media_type: {}}}
    unmarshaled = unmarshaler.unmarshal(
        get_value, media_type, request_body_spec_dict
    )
    assert unmarshaled == 'foo'


def test_unmarshal_success(unmarshaler, media_type):
    def get_value():
        return '2018-01-02'

    request_body_spec_dict = {
        'content': {
            media_type: {'schema': {'type': 'string', 'format': 'date'}}
        }
    }
    unmarshaled = unmarshaler.unmarshal(
        get_value, media_type, request_body_spec_dict
    )
    assert unmarshaled == datetime.date(2018, 1, 2)


def test_unmarshal_error(unmarshaler, media_type):
    def get_value():
        return str('2018/01/02')

    request_body_spec_dict = {
        'content': {
            media_type: {'schema': {'type': 'string', 'format': str('date')}}
        }
    }
    with pytest.raises(RequestBodyError) as exc_info:
        unmarshaler.unmarshal(get_value, media_type, request_body_spec_dict)

    errors = exc_info.value.errors
    assert errors[0].message == "'2018/01/02' is not a 'date'"
