from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict

import jsonschema

from ..exceptions import ValidationError
from .deserializers import deserialize_parameter

logger = logging.getLogger(__name__)


class ParametersUnmarshaler(object):
    def __init__(self, schema_unmarshaler):
        self._unmarshal_schema = schema_unmarshaler.unmarshal

    def unmarshal(self, values, parameter_spec_dicts):
        non_confidential_values = {
            'query': values.get('query'),
            'path': values.get('path'),
        }
        logger.info('Request parameters: %r', non_confidential_values)

        unmarshaled = defaultdict(dict)
        errors = []

        for index, parameter_spec_dict in enumerate(parameter_spec_dicts):
            name = parameter_spec_dict['name']
            location = parameter_spec_dict['in']

            try:
                value, schema = deserialize_parameter(
                    values, location, name, parameter_spec_dict
                )
            except KeyError:
                if parameter_spec_dict.get('required', False):
                    error = jsonschema.ValidationError(
                        '{!r} is a required in {!r} parameter'.format(
                            name, location
                        ),
                        validator='required',
                        validator_value=True,
                        schema=parameter_spec_dict,
                        schema_path=(index, 'required'),
                        path=(location, name),
                    )
                    errors.append(error)
            else:
                try:
                    value = self._unmarshal_schema(value, schema)
                except ValidationError as e:
                    for error in e.errors:
                        error.schema_path.extendleft(('schema', index))
                        error.path.extendleft([name, location])
                    errors.extend(e.errors)
                else:
                    unmarshaled[location][name] = value

        return unmarshaled, errors or None
