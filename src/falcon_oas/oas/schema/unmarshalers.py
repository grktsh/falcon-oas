from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import iteritems

from ..exceptions import ValidationError
from ..utils import cached_property
from .formats import default_formats
from .validators import SchemaValidator


class SchemaUnmarshaler(object):
    def __init__(self, spec=None, formats=None):
        if formats is None:
            formats = default_formats

        self._spec = spec
        self._formats = formats

    def unmarshal(self, instance, schema):
        """Validate and unmarshal the instance with the schema.

        :meth:`~._unmarshal` can assume the validated instance.
        """
        self._validator.validate(instance, schema)
        return self._unmarshal(instance, schema)

    @cached_property
    def _validator(self):
        return SchemaValidator(
            self._spec.data if self._spec is not None else {},
            format_checker=self._formats.format_checker,
        )

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
            return instance
        else:
            return handler(self, instance, schema)

    def _unmarshal_array(self, instance, schema):
        # ``items`` MUST be present if the ``type`` is ``array``.
        return [self._unmarshal(x, schema['items']) for x in instance]

    def _unmarshal_object(self, instance, schema):
        try:
            properties = schema['properties']
        except KeyError:
            properties = {}

        additional_properties = schema.get('additionalProperties')
        if isinstance(additional_properties, dict):
            properties = dict(additional_properties, **properties)

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
            modifier = self._formats[schema['format']]
        except KeyError:
            return instance
        else:
            return modifier(instance)

    _unmarshalers = {
        'integer': _unmarshal_primitive,
        'number': _unmarshal_primitive,
        'boolean': _unmarshal_primitive,
        'string': _unmarshal_primitive,
        'array': _unmarshal_array,
        'object': _unmarshal_object,
    }
