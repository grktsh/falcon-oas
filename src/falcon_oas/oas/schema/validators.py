from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from jsonschema import Draft4Validator
from jsonschema import FormatChecker
from jsonschema import validators
from six import integer_types
from six import iteritems
from six import string_types

from ..exceptions import ValidationError
from .formats import DEFAULT_FORMATS


_primitive_types = {
    'integer': integer_types,
    'number': float,
    'boolean': bool,
    'string': string_types,
}

_type_draft4_validator = Draft4Validator.VALIDATORS['type']


def _type_validator(validator, types, instance, schema):
    if instance is None and schema.get('nullable'):
        return

    for error in _type_draft4_validator(validator, types, instance, schema):
        yield error


_Validator = validators.extend(Draft4Validator, {'type': _type_validator})


class SchemaValidator(object):
    def __init__(self, formats=None):
        self._format_checker = _create_format_checker_from_formats(
            formats=formats
        )

    def validate(self, instance, schema):
        validator = _Validator(schema, format_checker=self._format_checker)
        errors = list(validator.iter_errors(instance))
        if errors:
            raise ValidationError(errors)


def _create_format_checker_from_formats(formats=None):
    if formats is None:
        formats = DEFAULT_FORMATS

    format_checker = FormatChecker(formats=())
    for schema_type, type_formats in iteritems(formats):
        for name, validator in iteritems(type_formats):
            checker = _to_checker(schema_type, validator)
            format_checker.checks(name, raises=ValueError)(checker)

    return format_checker


def _to_checker(schema_type, validator):
    types = _primitive_types[schema_type]

    def checker(instance):
        if not isinstance(instance, types):
            # Let type validator handle the type error
            return True
        # ``validator`` raises ValueError when format error
        validator(instance)
        return True

    return checker
