from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import functools

DEFAULT_PARSERS = {
    'date': lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date()
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
