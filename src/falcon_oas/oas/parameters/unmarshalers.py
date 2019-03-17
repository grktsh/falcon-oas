from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict

import jsonschema

from ..exceptions import ValidationError
from ..utils import pretty_json
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
        logger.info(
            'Request parameters: %s', pretty_json(non_confidential_values)
        )

        unmarshaled = defaultdict(dict)
        errors = []

        for index, parameter_spec_dict in enumerate(parameter_spec_dicts):
            name = parameter_spec_dict['name']
            location = parameter_spec_dict['in']
            schema = parameter_spec_dict.get('schema', {})

            try:
                value = self._get_value(values, location, name, schema)
            except KeyError:
                if parameter_spec_dict.get('required', False):
                    logger.warning(
                        'Missing parameter %r in %r', name, location
                    )
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
                    value = self._unmarshal(value, schema)
                except ValidationError as e:
                    logger.warning(
                        'Failed to unmarshal parameter %s with %s',
                        pretty_json(value),
                        pretty_json(schema),
                        exc_info=True,
                    )
                    for error in e.errors:
                        error.schema_path.extendleft(('schema', index))
                        error.path.extendleft([name, location])
                    errors.extend(e.errors)
                else:
                    unmarshaled[location][name] = value

        return unmarshaled, errors or None

    def _unmarshal(self, value, schema):
        value = deserialize_parameter(value, schema)
        value = self._unmarshal_schema(value, schema)
        return value

    def _get_value(self, values, location, name, schema):
        try:
            return values[location][name]
        except KeyError:
            # TODO: Support allOf, anyOf and oneOf
            return schema['default']
