from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from distutils.util import strtobool

parameter_deserializers = {
    'integer': int,
    'number': float,
    'boolean': strtobool,
}


def deserialize_parameter(value, schema):
    try:
        deserialize = parameter_deserializers[schema['type']]
    except KeyError:
        # array and object is unsupported yet
        return value

    try:
        return deserialize(value)
    except ValueError:
        # Let the validator to handle the type error
        return value
