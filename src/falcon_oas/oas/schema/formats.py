from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import base64
import binascii
import datetime
import functools

import jsonschema
from six import integer_types
from six import string_types

_primitive_types = {
    'integer': integer_types,
    'number': float,
    'boolean': bool,
    'string': string_types,
}


class Formats(object):
    def __init__(self):
        self.format_checker = jsonschema.FormatChecker(formats=())
        self._modifiers = {}

    def register(self, name, schema_type, raises=()):
        types = _primitive_types[schema_type]

        def decorator(modifier):
            @self.format_checker.checks(name, raises=raises)
            def func(instance):
                if not isinstance(instance, types):
                    # Let type validator handle the type error.
                    return True
                modifier(instance)
                return True

            self._modifiers[name] = modifier
            return modifier

        return decorator

    def __getitem__(self, name):
        return self._modifiers[name]


default_formats = Formats()

_register = default_formats.register


def bounded(value, min_value, max_value):
    if not (min_value <= value <= max_value):
        raise ValueError(
            'Must be between {} and {}: {!r}'.format(
                min_value, max_value, value
            )
        )
    return value


_register('int32', 'integer', raises=ValueError)(
    functools.partial(bounded, min_value=-2 ** 31, max_value=2 ** 31 - 1)
)
_register('int64', 'integer', raises=ValueError)(
    functools.partial(bounded, min_value=-2 ** 63, max_value=2 ** 63 - 1)
)
_register('byte', 'string', raises=(ValueError, TypeError))(base64.b64decode)
_register('binary', 'string', raises=(ValueError, TypeError))(
    binascii.unhexlify
)


@_register('date', 'string', raises=ValueError)
def parse_date(value):
    return datetime.datetime.strptime(value, '%Y-%m-%d').date()


try:
    import pyrfc3339
except ImportError:  # pragma: no cover
    pyrfc3339 = None
else:
    _register('date-time', 'string', raises=ValueError)(
        functools.partial(pyrfc3339.parse, utc=True)
    )

try:
    import rfc3986
except ImportError:  # pragma: no cover
    rfc3986 = None
else:

    @_register('uri', 'string', raises=rfc3986.exceptions.RFC3986Exception)
    def parse_uri(value):
        uri = rfc3986.uri_reference(value)
        validator = rfc3986.validators.Validator().require_presence_of(
            'scheme', 'host'
        )
        validator.validate(uri)
        return value
