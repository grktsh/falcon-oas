from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .exceptions import MissingRequestBody
from .exceptions import RequestBodyError
from .exceptions import ValidationError


class RequestBodyUnmarshaler(object):
    def __init__(self, spec, validator, unmarshaler):
        self.spec = spec
        self.validator = validator
        self.unmarshaler = unmarshaler

    def unmarshal(self, get_value, media_type, request_body_spec_dict):
        try:
            value = get_value()
        except ValueError:
            # TODO: distinguish deserialization error from empty body error
            if request_body_spec_dict.get('required', False):
                raise MissingRequestBody(media_type)
            # Should return unique object instead of None?
            return None

        try:
            media_type_spec_dict = request_body_spec_dict['content'][
                media_type
            ]
        except KeyError:
            # Undocumented media type
            return value

        try:
            return self._unmarshal(value, media_type_spec_dict)
        except ValidationError as e:
            raise RequestBodyError(e.errors)

    def _unmarshal(self, value, media_type_spec_dict):
        try:
            schema = media_type_spec_dict['schema']
        except KeyError:
            # Undocumented schema
            return value

        schema = self.spec.deref(schema)
        self.validator.validate(value, schema)
        value = self.unmarshaler.unmarshal(value, schema)
        return value
