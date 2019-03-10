# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from falcon_oas.oas.schema.validators import SchemaValidator
from falcon_oas.oas.schema.validators import ValidationError


@pytest.fixture
def schema():
    return {'type': str('string')}


def test_validate_success(schema):
    instance = 'foo'
    try:
        SchemaValidator().validate(instance, schema)
    except ValidationError as e:
        pytest.fail('Unexpected error: {}'.format(e))


def test_validate_error(schema):
    instance = 123
    message = "123 is not of type 'string'"

    with pytest.raises(ValidationError) as exc_info:
        SchemaValidator().validate(instance, schema)

    assert exc_info.value.errors[0].message == message


def test_validate_format_string(schema):
    schema['format'] = 'date'
    instance = '2018-01-02'
    try:
        SchemaValidator().validate(instance, schema)
    except ValidationError as e:
        pytest.fail('Unexpected error: {}'.format(e))


def test_validate_format_string_error(schema):
    schema['format'] = str('date')
    instance = str('2018/01/02')
    message = "'2018/01/02' is not a 'date'"

    with pytest.raises(ValidationError) as exc_info:
        SchemaValidator().validate(instance, schema)

    assert exc_info.value.errors[0].message == message


@pytest.mark.parametrize('instance', [-2 ** 31, 0, 2 ** 31 - 1])
def test_validate_format_integer(schema, instance):
    schema['type'] = 'integer'
    schema['format'] = 'int32'
    try:
        SchemaValidator().validate(instance, schema)
    except ValidationError as e:
        pytest.fail('Unexpected error: {}'.format(e))


@pytest.mark.parametrize('instance', [-2 ** 31 - 1, 2 ** 31])
def test_validate_format_integer_error(schema, instance):
    schema['type'] = 'integer'
    schema['format'] = str('int32')

    with pytest.raises(ValidationError) as exc_info:
        SchemaValidator().validate(instance, schema)

    assert exc_info.value.errors[0].message == "{} is not a 'int32'".format(
        instance
    )


def test_validate_without_formats(schema):
    schema['format'] = 'date'
    instance = '2018/01/02'
    try:
        SchemaValidator(formats={}).validate(instance, schema)
    except ValidationError as e:
        pytest.fail('Unexpected error: {}'.format(e))


def test_validate_format_non_string(schema):
    schema['format'] = 'date'
    instance = 123
    message = "123 is not of type 'string'"

    with pytest.raises(ValidationError) as exc_info:
        SchemaValidator().validate(instance, schema)

    assert exc_info.value.errors[0].message == message


@pytest.mark.parametrize(
    'instance,nullable', [('foo', False), ('foo', True), (None, True)]
)
def test_validate_nullable_success(schema, instance, nullable):
    schema['nullable'] = nullable
    try:
        SchemaValidator().validate(instance, schema)
    except ValidationError as e:
        pytest.fail('Unexpected error: {}'.format(e))


def test_validate_nullable_error(schema):
    schema['nullable'] = False
    instance = None

    with pytest.raises(ValidationError) as exc_info:
        SchemaValidator().validate(instance, schema)

    assert exc_info.value.errors[0].message == "None is not of type 'string'"


def test_validate_nullable_with_format(schema):
    schema['format'] = 'date'
    schema['nullable'] = True
    instance = None

    try:
        SchemaValidator().validate(instance, schema)
    except ValidationError as e:
        pytest.fail('Unexpected error: {}'.format(e))
