from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from distutils.util import strtobool

_parsers = {
    'integer': int,
    'number': float,
    'boolean': strtobool,
    'string': lambda x: x,
}


# TODO: Support style and explode
def deserialize_parameter(parameters, location, name, parameter_spec_dict):
    try:
        value = getattr(parameters, location)[name]
    except (AttributeError, KeyError):
        schema = parameter_spec_dict['schema']
        return schema['default'], schema

    try:
        schema = parameter_spec_dict['schema']
        schema_type = schema['type']
    except KeyError:
        return value, {}

    try:
        parser = _parsers[schema_type]
        return parser(value), schema
    except (KeyError, ValueError):
        # Let the validator handle the error
        return value, schema
