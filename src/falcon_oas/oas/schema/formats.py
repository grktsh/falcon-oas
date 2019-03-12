from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import base64
import binascii
import datetime
import functools


def raises(error):
    """Return a decorator to wrap the error with ValueError."""

    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except error as e:
                raise ValueError(e)

        return wrapper

    return decorator


def bounded(value, min_value, max_value):
    if not (min_value <= value <= max_value):
        raise ValueError(
            'Must be between {} and {}: {!r}'.format(
                min_value, max_value, value
            )
        )
    return value


def parse_date(value):
    return datetime.datetime.strptime(value, '%Y-%m-%d').date()


# The format modifier/validator can assume the type of the value is
# valid and modify it to any type.  When it raises ValueError it will
# be handled as ``format`` error by jsonschema.
DEFAULT_FORMATS = {
    'integer': {
        'int32': functools.partial(
            bounded, min_value=-2 ** 31, max_value=2 ** 31 - 1
        ),
        'int64': functools.partial(
            bounded, min_value=-2 ** 63, max_value=2 ** 63 - 1
        ),
    },
    'string': {
        'date': parse_date,
        'byte': raises(TypeError)(base64.b64decode),
        'binary': raises(TypeError)(binascii.unhexlify),
    },
}


try:
    import pyrfc3339
except ImportError:  # pragma: no cover
    pyrfc3339 = None
else:
    DEFAULT_FORMATS['string']['date-time'] = functools.partial(
        pyrfc3339.parse, utc=True
    )

try:
    import rfc3986
except ImportError:  # pragma: no cover
    rfc3986 = None
else:

    @raises(rfc3986.exceptions.RFC3986Exception)
    def parse_uri(value):
        uri = rfc3986.uri_reference(value)
        validator = rfc3986.validators.Validator().require_presence_of(
            'scheme', 'host'
        )
        validator.validate(uri)
        return value

    DEFAULT_FORMATS['string']['uri'] = parse_uri
