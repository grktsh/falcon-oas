from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import functools

DEFAULT_PARSERS = {
    'date': lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date()
}

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

    def create_uri_parser():
        validator = rfc3986.validators.Validator().require_presence_of(
            'scheme', 'host'
        )

        def parse_uri(value):
            try:
                validator.validate(rfc3986.uri_reference(value))
            except rfc3986.exceptions.RFC3986Exception as e:
                raise ValueError(e)
            return value

        return parse_uri

    DEFAULT_PARSERS['uri'] = create_uri_parser()
