from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from jsonschema import Draft4Validator
from jsonschema import validators

from ..exceptions import ValidationError

_type_draft4_validator = Draft4Validator.VALIDATORS['type']


def _type_validator(validator, types, instance, schema):
    if instance is None and schema.get('nullable'):
        return

    for error in _type_draft4_validator(validator, types, instance, schema):
        yield error


_enum_draft4_validator = Draft4Validator.VALIDATORS['enum']


def _enum_validator(validator, enums, instance, schema):
    if instance is None and schema.get('nullable'):
        return

    for error in _enum_draft4_validator(validator, enums, instance, schema):
        yield error


_Validator = validators.extend(
    Draft4Validator, {'type': _type_validator, 'enum': _enum_validator}
)


class SchemaValidator(object):
    def __init__(self, schema, format_checker=None):
        self._validator = _Validator(schema, format_checker=format_checker)

    def validate(self, instance, schema):
        errors = list(self._validator.iter_errors(instance, schema))
        if errors:
            raise ValidationError(errors)
