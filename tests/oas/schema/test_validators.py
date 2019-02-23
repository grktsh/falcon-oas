# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from falcon_oas.oas.schema.validators import SchemaValidator
from falcon_oas.oas.schema.validators import ValidationError
from falcon_oas.oas.spec import create_spec_from_dict


@pytest.fixture
def schema():
    return {'type': str('string')}


@pytest.fixture
def spec(schema):
    return create_spec_from_dict({'a': {'b': schema}})


def test_validate_success(spec, schema):
    instance = 'foo'
    try:
        SchemaValidator(spec).validate(instance, schema)
    except ValidationError as e:
        pytest.fail('Unexpected error: {}'.format(e))


def test_validate_error(spec, schema):
    instance = 123
    message = "123 is not of type 'string'"

    with pytest.raises(ValidationError) as exc_info:
        SchemaValidator(spec).validate(instance, schema)

    assert exc_info.value.errors[0].message == message


def test_validate_format(spec, schema):
    schema['format'] = 'date'
    instance = '2018-01-02'
    try:
        SchemaValidator(spec).validate(instance, schema)
    except ValidationError as e:
        pytest.fail('Unexpected error: {}'.format(e))


def test_validate_format_error(spec, schema):
    schema['format'] = str('date')
    instance = str('2018/01/02')
    message = "'2018/01/02' is not a 'date'"

    with pytest.raises(ValidationError) as exc_info:
        SchemaValidator(spec).validate(instance, schema)

    assert exc_info.value.errors[0].message == message


def test_validate_without_parsers(spec, schema):
    schema['format'] = 'date'
    instance = '2018/01/02'
    try:
        SchemaValidator(spec, parsers={}).validate(instance, schema)
    except ValidationError as e:
        pytest.fail('Unexpected error: {}'.format(e))


def test_validate_format_non_string(spec, schema):
    schema['format'] = 'date'
    instance = 123
    message = "123 is not of type 'string'"

    with pytest.raises(ValidationError) as exc_info:
        SchemaValidator(spec).validate(instance, schema)

    assert exc_info.value.errors[0].message == message


@pytest.mark.parametrize(
    'instance,nullable', [('foo', False), ('foo', True), (None, True)]
)
def test_validate_nullable_success(spec, schema, instance, nullable):
    schema['nullable'] = nullable
    try:
        SchemaValidator(spec).validate(instance, schema)
    except ValidationError as e:
        pytest.fail('Unexpected error: {}'.format(e))


def test_validate_nullable_error(spec, schema):
    schema['nullable'] = False
    instance = None

    with pytest.raises(ValidationError) as exc_info:
        SchemaValidator(spec).validate(instance, schema)

    assert exc_info.value.errors[0].message == "None is not of type 'string'"


def test_validate_nullable_with_format(spec, schema):
    schema['format'] = 'date'
    schema['nullable'] = True
    instance = None

    try:
        SchemaValidator(spec).validate(instance, schema)
    except ValidationError as e:
        pytest.fail('Unexpected error: {}'.format(e))
