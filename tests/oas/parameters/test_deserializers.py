from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from falcon_oas.oas.parameters.deserializers import deserialize_parameter


def test_deserialize_parameter_default(mocker):
    location = 'query'
    name = 'p'
    parameters = mocker.MagicMock(**{location: {}})
    parameter_spec_dict = {'schema': {'default': 42}}

    result = deserialize_parameter(
        parameters, location, name, parameter_spec_dict
    )
    assert result == (42, parameter_spec_dict['schema'])


@pytest.mark.parametrize('parameter_spec_dict', [{}, {'schema': {}}])
def test_deserialize_parameter_no_default(mocker, parameter_spec_dict):
    location = 'query'
    name = 'p'
    parameters = mocker.MagicMock(**{location: {}})

    pytest.raises(
        KeyError,
        deserialize_parameter,
        parameters,
        location,
        name,
        parameter_spec_dict,
    )


@pytest.mark.parametrize(
    'value,parameter_spec_dict', [('2', {}), ('2', {'schema': {}})]
)
def test_deserialize_parameter_no_schema_or_type(
    mocker, value, parameter_spec_dict
):
    location = 'query'
    name = 'p'
    parameters = mocker.MagicMock(**{location: {name: value}})

    result = deserialize_parameter(
        parameters, location, name, parameter_spec_dict
    )
    assert result == (value, {})


@pytest.mark.parametrize(
    'value,schema_type,expected_value',
    [
        ('2', 'integer', 2),
        ('2.3', 'number', 2.3),
        ('2', 'number', 2.0),
        ('1', 'boolean', True),
        ('0', 'boolean', False),
        ('true', 'boolean', True),
        ('false', 'boolean', False),
        ('t', 'boolean', True),
        ('f', 'boolean', False),
        ('yes', 'boolean', True),
        ('no', 'boolean', False),
        ('x', 'string', 'x'),
    ],
)
def test_deserialize_parameter_parse_success(
    mocker, value, schema_type, expected_value
):
    location = 'query'
    name = 'p'
    parameters = mocker.MagicMock(**{location: {name: value}})
    parameter_spec_dict = {'schema': {'type': schema_type}}

    result = deserialize_parameter(
        parameters, location, name, parameter_spec_dict
    )
    assert result == (expected_value, parameter_spec_dict['schema'])


@pytest.mark.parametrize(
    'value,schema_type',
    [
        ('x', 'integer'),
        ('2.3', 'integer'),
        ('x', 'number'),
        ('2', 'boolean'),
        ('x', 'boolean'),
        ('{}', 'object'),  # Unsupported yet
        ('[]', 'array'),  # Unsupported yet
    ],
)
def test_deserialize_parameter_parse_error(mocker, value, schema_type):
    location = 'query'
    name = 'p'
    parameters = mocker.MagicMock(**{location: {name: value}})
    parameter_spec_dict = {'schema': {'type': schema_type}}

    result = deserialize_parameter(
        parameters, location, name, parameter_spec_dict
    )
    assert result == (value, parameter_spec_dict['schema'])
