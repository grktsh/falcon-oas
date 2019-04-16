# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

import pytest

from falcon_oas.oas.exceptions import ValidationError
from falcon_oas.oas.schema.formats import Formats
from falcon_oas.oas.schema.unmarshalers import SchemaUnmarshaler


def test_unmarshal_validation_error():
    schema = {'type': str('string')}
    instance = 123
    message = "123 is not of type 'string'"

    with pytest.raises(ValidationError) as exc_info:
        SchemaUnmarshaler().unmarshal(instance, schema)
    assert exc_info.value.errors[0].message == message


@pytest.mark.parametrize(
    'schema,instance',
    [
        ({'type': 'boolean'}, True),
        ({'type': 'boolean'}, False),
        ({'type': 'number'}, 0.0),
        ({'type': 'number'}, 2.0),
        ({'type': 'integer'}, 0),
        ({'type': 'integer'}, 2),
        ({'type': 'string'}, 'foo'),
    ],
)
def test_unmarshal_primitive(schema, instance):
    unmarshaled = SchemaUnmarshaler().unmarshal(instance, schema)
    assert unmarshaled == instance


def test_unmarshal_primitive_format():
    schema = {'type': 'string', 'format': 'date'}
    instance = '2018-01-02'
    unmarshaled = SchemaUnmarshaler().unmarshal(instance, schema)
    assert unmarshaled == datetime.date(2018, 1, 2)


def test_unmarshal_primitive_without_formats():
    schema = {'type': 'string', 'format': 'date'}
    instance = '2018-01-02'
    unmarshaled = SchemaUnmarshaler(formats=Formats()).unmarshal(
        instance, schema
    )
    assert unmarshaled == instance


def test_unmarshal_primitive_enum():
    schema = {'type': 'string', 'enum': ['a', 'b']}
    instance = 'a'
    unmarshaled = SchemaUnmarshaler().unmarshal(instance, schema)
    assert unmarshaled == 'a'


def test_unmarshal_array():
    schema = {'type': 'array', 'items': {'type': 'string', 'format': 'date'}}
    instance = ['2018-01-02', '2018-02-03', '2018-03-04']
    unmarshaled = SchemaUnmarshaler().unmarshal(instance, schema)
    assert unmarshaled == [
        datetime.date(2018, 1, 2),
        datetime.date(2018, 2, 3),
        datetime.date(2018, 3, 4),
    ]


def test_unmarshal_object():
    schema = {
        'type': 'object',
        'properties': {
            'id': {'type': 'integer'},
            'date': {'type': 'string', 'format': 'date'},
            'date-default': {
                'type': 'string',
                'format': 'date',
                'default': '2020-01-01',
            },
        },
    }
    instance = {'date': '2018-01-02'}
    unmarshaled = SchemaUnmarshaler().unmarshal(instance, schema)
    assert unmarshaled == {
        'date': datetime.date(2018, 1, 2),
        'date-default': datetime.date(2020, 1, 1),
    }


@pytest.mark.parametrize(
    'properties,additional_properties,expected',
    [
        (None, None, {}),
        (None, True, {}),
        (None, {}, {}),
        (None, {'x': {'type': 'string'}}, {'x': 'foo'}),
        ({'x': {'type': 'string'}}, None, {'x': 'foo'}),
        ({'x': {'type': 'string'}}, True, {'x': 'foo'}),
        ({'x': {'type': 'string'}}, {}, {'x': 'foo'}),
        ({'x': {'type': 'string'}}, {'x': {'type': 'integer'}}, {'x': 'foo'}),
    ],
)
def test_unmarshal_object_properties_and_additional_properties(
    properties, additional_properties, expected
):
    schema = {'type': 'object'}
    if properties is not None:
        schema['properties'] = properties
    if additional_properties is not None:
        schema['additionalProperties'] = additional_properties

    instance = {'x': 'foo'}
    unmarshaled = SchemaUnmarshaler().unmarshal(instance, schema)
    assert unmarshaled == expected


def test_unmarshal_all_of():
    schema = {
        'allOf': [
            {'type': 'object', 'properties': {'id': {'type': 'integer'}}},
            {'type': 'object', 'properties': {'date': {'type': 'string'}}},
            {
                'type': 'object',
                'properties': {'date': {'type': 'string', 'format': 'date'}},
            },
        ]
    }
    instance = {'id': 2, 'date': '2018-01-02'}
    unmarshaled = SchemaUnmarshaler().unmarshal(instance, schema)
    assert unmarshaled == {'id': 2, 'date': datetime.date(2018, 1, 2)}


def test_unmarshal_all_of_required_only():
    schema = {
        'allOf': [
            {'type': 'object', 'properties': {'id': {'type': 'integer'}}},
            {'type': 'object', 'required': [str('id')]},
        ]
    }
    instance = {}
    with pytest.raises(ValidationError) as exc_info:
        SchemaUnmarshaler().unmarshal(instance, schema)
    assert exc_info.value.errors[0].message == "'id' is a required property"


@pytest.mark.parametrize('schema_type', ['oneOf', 'anyOf'])
def test_unmarshal_one_of_or_any_of(schema_type):
    schema = {
        schema_type: [
            {'type': 'integer'},
            {'type': 'string', 'format': 'date'},
        ]
    }
    instance = '2018-01-02'
    unmarshaled = SchemaUnmarshaler().unmarshal(instance, schema)
    assert unmarshaled == datetime.date(2018, 1, 2)


@pytest.mark.parametrize(
    'schema',
    [
        {'type': 'string', 'nullable': True},
        {'type': 'array', 'nullable': True},
        {'type': 'object', 'nullable': True},
        {'type': 'string', 'format': 'date', 'nullable': True},
        {'type': 'string', 'enum': ['a', 'b'], 'nullable': True},
    ],
)
def test_unmarshal_nullable(schema):
    instance = None
    unmarshaled = SchemaUnmarshaler().unmarshal(instance, schema)
    assert unmarshaled is None
