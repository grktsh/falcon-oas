from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from jsonschema import Draft4Validator
from jsonschema import FormatChecker
from jsonschema import validators
from six import iteritems
from six import string_types

from ..exceptions import ValidationError
from .parsers import DEFAULT_PARSERS


_type_draft4_validator = Draft4Validator.VALIDATORS['type']


def _type_validator(validator, types, instance, schema):
    if instance is None and schema.get('nullable'):
        return

    for error in _type_draft4_validator(validator, types, instance, schema):
        yield error


_Validator = validators.extend(Draft4Validator, {'type': _type_validator})


class SchemaValidator(object):
    def __init__(self, spec, parsers=None):
        self.spec_dict = spec.spec_dict
        self.format_checker = _create_format_checker_from_parsers(parsers)

    def validate(self, instance, schema):
        validator = self._create_validator()
        errors = list(validator.iter_errors(instance, _schema=schema))
        if errors:
            raise ValidationError(errors)

    def _create_validator(self):
        return _Validator(self.spec_dict, format_checker=self.format_checker)


def _create_format_checker_from_parsers(parsers=None):
    if parsers is None:
        parsers = DEFAULT_PARSERS

    format_checker = FormatChecker(formats=())
    for format_, parser in iteritems(parsers):
        checker = _to_checker(parser)
        format_checker.checks(format_, raises=ValueError)(checker)

    return format_checker


def _to_checker(parser):
    def checker(instance):
        if not isinstance(instance, string_types):
            return True
        return parser(instance)

    return checker
