from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict

from ..exceptions import MissingParameter
from ..exceptions import ParameterError
from ..exceptions import ParametersError
from ..exceptions import ValidationError
from ..utils import pretty_json
from .deserializers import deserialize_parameter

logger = logging.getLogger(__name__)


class ParametersUnmarshaler(object):
    def __init__(self, unmarshaler):
        self.unmarshaler = unmarshaler

    def unmarshal(self, values, parameters):
        non_confidential_values = {
            'query': values.get('query'),
            'path': values.get('path'),
        }
        logger.info(
            'Request parameters: %s', pretty_json(non_confidential_values)
        )

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
                    logger.warning(
                        'Missing parameter %r in %r', name, location
                    )
                    errors.append(MissingParameter(name, location))
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
                    errors.append(ParameterError(name, location, e.errors))
                else:
                    unmarshaled[location][name] = value

        if errors:
            raise ParametersError(errors)
        return unmarshaled

    def _unmarshal(self, value, schema):
        value = deserialize_parameter(value, schema)
        value = self.unmarshaler.unmarshal(value, schema)
        return value

    def _get_value(self, values, location, name, schema):
        try:
            return values[location][name]
        except KeyError:
            # TODO: Support allOf, anyOf and oneOf
            return schema['default']
