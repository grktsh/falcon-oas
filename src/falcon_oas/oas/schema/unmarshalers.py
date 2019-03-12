from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from six import iteritems

from ..exceptions import ValidationError
from .formats import DEFAULT_FORMATS
from .validators import SchemaValidator

logger = logging.getLogger(__name__)


class SchemaUnmarshaler(object):
    def __init__(self, formats=None):
        if formats is None:
            self.formats = DEFAULT_FORMATS
        else:
            self.formats = formats

        self._validate = SchemaValidator(formats=self.formats).validate
        self._unmarshalers = {
            'array': self._unmarshal_array,
            'object': self._unmarshal_object,
        }

    def unmarshal(self, instance, schema):
        """Validate and unmarshal the instance with the schema.

        ``self._unmarshal`` can assume the validated instance.
        """
        self._validate(instance, schema)
        return self._unmarshal(instance, schema)

    def _unmarshal(self, instance, schema):
        if instance is None:
            # Support nullable value
            return instance

        if 'allOf' in schema:
            # If multiple sub schemas define same property latter wins.
            return {
                k: v
                for sub_schema in schema['allOf']
                for k, v in iteritems(self._unmarshal(instance, sub_schema))
            }

        for sub_schema in schema.get('oneOf') or schema.get('anyOf') or []:
            try:
                # TODO: Remove duplicate validation
                return self.unmarshal(instance, sub_schema)
            except ValidationError:
                pass

        try:
            handler = self._unmarshalers[schema['type']]
        except KeyError:
            handler = self._unmarshal_primitive
        return handler(instance, schema)

    def _unmarshal_array(self, instance, schema):
        # ``items`` MUST be present if the ``type`` is ``array``.
        return [self._unmarshal(x, schema['items']) for x in instance]

    def _unmarshal_object(self, instance, schema):
        try:
            properties = schema['properties']
        except KeyError:
            # Omitting properties keyword has the same behavior as an
            # empty object.
            return {}

        result = {}
        for name, sub_schema in iteritems(properties):
            try:
                value = instance[name]
            except KeyError:
                try:
                    value = sub_schema['default']
                except KeyError:
                    continue
            result[name] = self._unmarshal(value, sub_schema)
        return result

    def _unmarshal_primitive(self, instance, schema):
        try:
            modifier = self.formats[schema['type']][schema['format']]
        except KeyError:
            return instance
        else:
            return modifier(instance)
