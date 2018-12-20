from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from .exceptions import MissingRequestBody
from .exceptions import RequestBodyError
from .exceptions import ValidationError
from .utils import pretty_json

logger = logging.getLogger(__name__)


class RequestBodyUnmarshaler(object):
    def __init__(self, unmarshaler):
        self.unmarshaler = unmarshaler

    def unmarshal(self, get_value, media_type, request_body_spec_dict):
        try:
            value = get_value()
        except ValueError:
            # TODO: distinguish deserialization error from empty body error
            logger.warning(
                'Request body is empty or corrupted for media type: %s',
                media_type,
                exc_info=True,
            )
            if request_body_spec_dict.get('required', False):
                raise MissingRequestBody(media_type)
            # Should return unique object instead of None?
            return None

        # TODO: Obscure confidential data
        logger.info(
            'Media type: %s, request body: %s', media_type, pretty_json(value)
        )

        media_type_spec_dict = request_body_spec_dict['content'][media_type]
        try:
            return self._unmarshal(value, media_type_spec_dict)
        except ValidationError as e:
            logger.warning(
                'Failed to unmarshal request body %s with %s',
                pretty_json(value),
                pretty_json(media_type_spec_dict),
                exc_info=True,
            )
            raise RequestBodyError(e.errors)

    def _unmarshal(self, value, media_type_spec_dict):
        try:
            schema = media_type_spec_dict['schema']
        except KeyError:
            logger.warning('Missing schema')
            return value

        value = self.unmarshaler.unmarshal(value, schema)
        return value
