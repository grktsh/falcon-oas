# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

import pytest

from falcon_oas.oas.exceptions import ParametersError
from falcon_oas.oas.parameters.unmarshalers import ParametersUnmarshaler
from falcon_oas.oas.schema.unmarshalers import SchemaUnmarshaler
from falcon_oas.oas.spec import create_spec_from_dict


@pytest.fixture
def unmarshaler():
    spec = create_spec_from_dict({})
    unmarshaler = SchemaUnmarshaler(spec)
    return ParametersUnmarshaler(unmarshaler)


def test_missing(unmarshaler):
    values = {}
    parameter_spec_dict_list = [
        {'name': 'param1', 'in': 'query', 'required': True},
        {'name': 'param2', 'in': 'query', 'required': True},
        {'name': 'param3', 'in': 'query'},
    ]
    with pytest.raises(ParametersError) as exc_info:
        unmarshaler.unmarshal(values, parameter_spec_dict_list)

    assert len(exc_info.value.errors) == 2
    assert exc_info.value.errors[0].name == 'param1'
    assert exc_info.value.errors[1].name == 'param2'


def test_default(unmarshaler):
    values = {}
    parameter_spec_dict_list = [
        {'name': 'param1', 'in': 'query', 'schema': {'default': 123}},
        {
            'name': 'param2',
            'in': 'query',
            'required': True,
            'schema': {'default': 'x'},
        },
    ]
    unmarshaled = unmarshaler.unmarshal(values, parameter_spec_dict_list)

    assert unmarshaled == {'query': {'param1': 123, 'param2': 'x'}}


def test_undocumented_schema(unmarshaler):
    values = {'query': {'param1': 'foo'}}
    parameter_spec_dict_list = [{'name': 'param1', 'in': 'query'}]
    unmarshaled = unmarshaler.unmarshal(values, parameter_spec_dict_list)

    assert unmarshaled == values


def test_unmarshal_success(unmarshaler):
    values = {'query': {'param1': '2018-01-02'}}
    parameter_spec_dict_list = [
        {
            'name': 'param1',
            'in': 'query',
            'schema': {'type': 'string', 'format': 'date'},
        }
    ]
    unmarshaled = unmarshaler.unmarshal(values, parameter_spec_dict_list)

    assert unmarshaled == {'query': {'param1': datetime.date(2018, 1, 2)}}


def test_unmarshal_error(unmarshaler):
    values = {'query': {'param1': str('2018/01/02')}}
    parameter_spec_dict_list = [
        {
            'name': 'param1',
            'in': 'query',
            'schema': {'type': 'string', 'format': str('date')},
        }
    ]
    with pytest.raises(ParametersError) as exc_info:
        unmarshaler.unmarshal(values, parameter_spec_dict_list)

    errors = exc_info.value.errors
    assert errors[0].errors[0].message == "'2018/01/02' is not a 'date'"
