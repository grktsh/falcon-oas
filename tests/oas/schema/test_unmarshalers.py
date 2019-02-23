# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

import pytest
import pytz

from falcon_oas.oas.exceptions import ValidationError
from falcon_oas.oas.schema.unmarshalers import SchemaUnmarshaler
from falcon_oas.oas.spec import create_spec_from_dict


@pytest.fixture
def schema():
    return {}


@pytest.fixture
def spec(schema):
    return create_spec_from_dict({})


def test_unmarshal_validation_error(spec, schema):
    schema['type'] = str('string')
    instance = 123
    message = "123 is not of type 'string'"

    with pytest.raises(ValidationError) as exc_info:
        SchemaUnmarshaler(spec).unmarshal(instance, schema)

    assert exc_info.value.errors[0].message == message


@pytest.mark.parametrize(
    'schema_type,instance',
    [
        ('boolean', True),
        ('boolean', False),
        ('number', 0.0),
        ('number', 2.0),
        ('integer', 0),
        ('integer', 2),
        ('string', 'foo'),
    ],
)
def test_unmarshal_atom(spec, schema, schema_type, instance):
    schema['type'] = schema_type
    unmarshaled = SchemaUnmarshaler(spec).unmarshal(instance, schema)
    assert unmarshaled == instance


def test_unmarshal_atom_format_date(spec, schema):
    schema.update({'type': 'string', 'format': 'date'})
    instance = '2018-01-02'
    unmarshaled = SchemaUnmarshaler(spec).unmarshal(instance, schema)
    assert unmarshaled == datetime.date(2018, 1, 2)


def test_unmarshal_atom_format_date_time(spec, schema):
    schema.update({'type': 'string', 'format': 'date-time'})
    instance = '2018-01-02T03:04:05Z'
    unmarshaled = SchemaUnmarshaler(spec).unmarshal(instance, schema)
    assert unmarshaled == datetime.datetime(
        2018, 1, 2, 3, 4, 5, tzinfo=pytz.utc
    )


def test_unmarshal_atom_format_uri(spec, schema):
    schema.update({'type': 'string', 'format': 'uri'})
    instance = 'http://example.com/path'
    unmarshaled = SchemaUnmarshaler(spec).unmarshal(instance, schema)
    assert unmarshaled == instance


def test_unmarshal_array(spec, schema):
    schema.update(
        {'type': 'array', 'items': {'type': 'string', 'format': 'date'}}
    )
    instance = ['2018-01-02', '2018-02-03', '2018-03-04']
    unmarshaled = SchemaUnmarshaler(spec).unmarshal(instance, schema)
    assert unmarshaled == [
        datetime.date(2018, 1, 2),
        datetime.date(2018, 2, 3),
        datetime.date(2018, 3, 4),
    ]


def test_unmarshal_object(spec, schema):
    schema.update(
        {
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
    )
    instance = {'date': '2018-01-02'}
    unmarshaled = SchemaUnmarshaler(spec).unmarshal(instance, schema)
    assert unmarshaled == {
        'date': datetime.date(2018, 1, 2),
        'date-default': datetime.date(2020, 1, 1),
    }


def test_unmarshal_object_without_properties(spec, schema):
    schema['type'] = 'object'
    instance = {'date': '2018-01-02'}
    unmarshaled = SchemaUnmarshaler(spec).unmarshal(instance, schema)
    assert unmarshaled == {}


def test_unmarshal_all_of(spec, schema):
    schema['allOf'] = [
        {'type': 'object', 'properties': {'id': {'type': 'integer'}}},
        {
            'type': 'object',
            'properties': {'date': {'type': 'string', 'format': 'date'}},
        },
    ]
    instance = {'id': 2, 'date': '2018-01-02'}
    unmarshaled = SchemaUnmarshaler(spec).unmarshal(instance, schema)
    assert unmarshaled == {'id': 2, 'date': datetime.date(2018, 1, 2)}


@pytest.mark.parametrize('schema_type', ['oneOf', 'anyOf'])
def test_unmarshal_one_of_or_any_of(spec, schema, schema_type):
    schema[schema_type] = [
        {'type': 'string', 'format': 'date'},
        {'type': 'integer'},
    ]
    instance = '2018-01-02'
    unmarshaled = SchemaUnmarshaler(spec).unmarshal(instance, schema)
    assert unmarshaled == instance


def test_unmarshal_without_parsers(spec, schema):
    schema.update({'type': 'string', 'format': 'date'})
    instance = '2018-01-02'
    unmarshaled = SchemaUnmarshaler(spec, parsers={}).unmarshal(
        instance, schema
    )
    assert unmarshaled == instance


@pytest.mark.parametrize(
    'schema',
    [
        {'type': 'string', 'nullable': True},
        {'type': 'array', 'nullable': True},
        {'type': 'object', 'nullable': True},
        {'type': 'string', 'format': 'date', 'nullable': True},
    ],
)
def test_unmarshal_nullable(spec, schema):
    instance = None
    unmarshaled = SchemaUnmarshaler(spec).unmarshal(instance, schema)
    assert unmarshaled is None
