from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import functools


def parse_int(value, min_int, max_int):
    n = int(value)
    if not (min_int <= n <= max_int):
        raise ValueError(
            'Must be between {} and {}: {!r}'.format(min_int, max_int, value)
        )
    return n


def parse_date(value):
    return datetime.datetime.strptime(value, '%Y-%m-%d').date()


DEFAULT_PARSERS = {
    'int32': functools.partial(
        parse_int, min_int=-2 ** 31, max_int=2 ** 31 - 1
    ),
    'int64': functools.partial(
        parse_int, min_int=-2 ** 63, max_int=2 ** 63 - 1
    ),
    'date': parse_date,
}


def raises(error):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except error as e:
                raise ValueError(e)

        return wrapper

    return decorator


try:
    import pyrfc3339
except ImportError:  # pragma: no cover
    pyrfc3339 = None
else:
    DEFAULT_PARSERS['date-time'] = functools.partial(pyrfc3339.parse, utc=True)

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

    DEFAULT_PARSERS['uri'] = parse_uri
