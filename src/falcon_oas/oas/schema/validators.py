from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from jsonschema import Draft4Validator
from jsonschema import validators

from ..exceptions import ValidationError
from .formats import default_formats

_type_draft4_validator = Draft4Validator.VALIDATORS['type']


def _type_validator(validator, types, instance, schema):
    if instance is None and schema.get('nullable'):
        return

    for error in _type_draft4_validator(validator, types, instance, schema):
        yield error


_Validator = validators.extend(Draft4Validator, {'type': _type_validator})


class SchemaValidator(object):
    def __init__(self, formats=None):
        if formats is None:
            formats = default_formats

        self._format_checker = formats.format_checker

    def validate(self, instance, schema):
        validator = _Validator(schema, format_checker=self._format_checker)
        errors = list(validator.iter_errors(instance))
        if errors:
            raise ValidationError(errors)
