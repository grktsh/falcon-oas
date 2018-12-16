from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict

from ..exceptions import MissingParameter
from ..exceptions import ParameterError
from ..exceptions import ParametersError
from ..exceptions import ValidationError
from .deserializers import deserialize_parameter


class ParametersUnmarshaler(object):
    def __init__(self, spec, validator, unmarshaler):
        self.spec = spec
        self.validator = validator
        self.unmarshaler = unmarshaler

    def unmarshal(self, values, parameters):
        unmarshaled = defaultdict(dict)
        errors = []

        for parameter_spec_dict in parameters:
            name = parameter_spec_dict['name']
            location = parameter_spec_dict['in']
            schema = parameter_spec_dict.get('schema', {})

            try:
                value = self._get_value(values, location, name, schema)
            except KeyError:
                if parameter_spec_dict.get('required', False):
                    errors.append(MissingParameter(name, location))
            else:
                try:
                    value = self._unmarshal(value, schema)
                except ValidationError as e:
                    errors.append(ParameterError(name, location, e.errors))
                else:
                    unmarshaled[location][name] = value

        if errors:
            raise ParametersError(errors)
        return unmarshaled

    def _unmarshal(self, value, schema):
        value = deserialize_parameter(value, schema)
        self.validator.validate(value, schema)
        value = self.unmarshaler.unmarshal(value, schema)
        return value

    def _get_value(self, values, location, name, schema):
        try:
            return values[location][name]
        except KeyError:
            # TODO: Support allOf, anyOf and oneOf
            return schema['default']
