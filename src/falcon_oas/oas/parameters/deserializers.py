from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
from distutils.util import strtobool

logger = logging.getLogger(__name__)

parameter_deserializers = {
    'integer': int,
    'number': float,
    'boolean': strtobool,
    'string': lambda x: x,
}


def deserialize_parameter(value, schema):
    try:
        schema_type = schema['type']
    except KeyError:
        logger.warning('Missing parameter schema type')
        return value

    try:
        deserialize = parameter_deserializers[schema_type]
    except KeyError:
        logger.warning('Unsupported parameter schema type: %r', schema_type)
        return value

    try:
        return deserialize(value)
    except ValueError:
        # Let the validator to handle the type error
        return value
