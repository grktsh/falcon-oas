# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
from collections import deque

import jsonschema
import pytest

from falcon_oas.oas.parameters.unmarshalers import ParametersUnmarshaler
from falcon_oas.oas.schema.unmarshalers import SchemaUnmarshaler


@pytest.fixture
def unmarshal():
    return ParametersUnmarshaler(SchemaUnmarshaler()).unmarshal


def test_missing(mocker, unmarshal):
    parameters = mocker.MagicMock(query={})
    parameter_spec_dict_list = [
        {'name': str('p1'), 'in': str('query'), 'required': True},
        {'name': 'p2', 'in': 'query'},
    ]

    _, errors = unmarshal(parameters, parameter_spec_dict_list)

    assert len(errors) == 1
    assert isinstance(errors[0], jsonschema.ValidationError)
    assert errors[0].message == "'p1' is a required in 'query' parameter"
    assert errors[0].validator == 'required'
    assert errors[0].validator_value is True
    assert errors[0].schema == parameter_spec_dict_list[0]
    assert errors[0].schema_path == deque([0, 'required'])
    assert errors[0].path == deque(['query', 'p1'])


def test_default(mocker, unmarshal):
    parameters = mocker.MagicMock(query={})
    parameter_spec_dict_list = [
        {'name': 'param1', 'in': 'query', 'schema': {'default': 123}},
        {
            'name': 'param2',
            'in': 'query',
            'required': True,
            'schema': {'default': 'x'},
        },
    ]
    unmarshaled, errors = unmarshal(parameters, parameter_spec_dict_list)

    assert unmarshaled == {'query': {'param1': 123, 'param2': 'x'}}
    assert errors is None


def test_undocumented_schema(mocker, unmarshal):
    parameters = mocker.MagicMock(query={'param1': 'foo'})
    parameter_spec_dict_list = [{'name': 'param1', 'in': 'query'}]
    unmarshaled, errors = unmarshal(parameters, parameter_spec_dict_list)

    assert unmarshaled == {'query': {'param1': 'foo'}}
    assert errors is None


def test_unmarshal_success(mocker, unmarshal):
    parameters = mocker.MagicMock(query={'param1': '2018-01-02'})
    parameter_spec_dict_list = [
        {
            'name': 'param1',
            'in': 'query',
            'schema': {'type': 'string', 'format': 'date'},
        }
    ]
    unmarshaled, errors = unmarshal(parameters, parameter_spec_dict_list)

    assert unmarshaled == {'query': {'param1': datetime.date(2018, 1, 2)}}
    assert errors is None


def test_unmarshal_error(mocker, unmarshal):
    parameters = mocker.MagicMock(query={'param1': str('2018/01/02')})
    parameter_spec_dict_list = [
        {
            'name': 'param1',
            'in': 'query',
            'schema': {'type': 'string', 'format': str('date')},
        }
    ]
    _, errors = unmarshal(parameters, parameter_spec_dict_list)

    assert len(errors) == 1
    assert isinstance(errors[0], jsonschema.ValidationError)
    assert errors[0].message == "'2018/01/02' is not a 'date'"
    assert errors[0].validator == 'format'
    assert errors[0].validator_value == 'date'
    assert errors[0].instance == '2018/01/02'
    assert errors[0].schema == {'type': 'string', 'format': str('date')}
    assert errors[0].schema_path == deque([0, 'schema', 'format'])
    assert errors[0].path == deque(['query', 'param1'])
