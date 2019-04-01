from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
from six import iteritems

from . import extensions
from .oas.request.models import Request
from .oas.request.unmarshalers import unmarshal_request
from .oas.schema.unmarshalers import SchemaUnmarshaler
from .oas.security import AccessControl
from .oas.utils import cached_property
from .utils import import_string


class _Indexer(object):
    def __init__(self, getter):
        self._getter = getter

    def __getitem__(self, key):
        try:
            return self._getter(key, required=True)
        except falcon.HTTPBadRequest:
            raise KeyError(key)

    def get(self, key, default=None):
        return self._getter(key, default=default)


class _RequestAdapter(Request):
    def __init__(self, req, params):
        self._req = req
        self._params = params

    @property
    def uri_template(self):
        return self._req.uri_template

    @property
    def method(self):
        return self._req.method.lower()

    @property
    def context(self):
        return self._req.context

    @property
    def path(self):
        return self._params

    @property
    def query(self):
        return self._req.params

    @cached_property
    def header(self):
        return _Indexer(self._req.get_header)

    # Use cached_property since Falcon 1 copies cookies every time.
    @cached_property
    def cookie(self):
        return self._req.cookies

    @property
    def content_length(self):
        return self._req.content_length or 0

    @property
    def media_type(self):
        content_type = self._req.content_type
        return content_type and content_type.split(';', 1)[0]

    @property
    def media(self):
        try:
            return self._req.media
        except ValueError as e:
            # Convert ValueError which Falcon 1 raises to
            # falcon.HTTPBadRequest which Falcon 2 raises.
            raise falcon.HTTPBadRequest(
                'Invalid JSON', 'Could not parse JSON body - {0}'.format(e)
            )


class _Context(object):
    __slots__ = ('schema_unmarshaler', 'user', 'parameters', 'request_body')

    def __init__(
        self, schema_unmarshaler, user=None, parameters=None, request_body=None
    ):
        self.schema_unmarshaler = schema_unmarshaler
        self.user = user
        self.parameters = parameters
        self.request_body = request_body


class Middleware(object):
    def __init__(self, spec, formats=None, base_module=''):
        self._spec = spec
        self._formats = formats
        security_schemes = _get_security_schemes(spec, base_module=base_module)
        self._access_control = AccessControl(security_schemes)

    def process_resource(self, req, resp, resource, params):
        oas_req = _RequestAdapter(req, params)

        operation = self._spec.get_operation(
            oas_req.uri_template, oas_req.method, oas_req.media_type
        )
        if operation is None:
            return

        schema_unmarshaler = SchemaUnmarshaler(
            spec=self._spec, formats=self._formats
        )
        req.context['oas'] = context = _Context(schema_unmarshaler)

        user = self._access_control.handle(oas_req, operation)

        parameters, request_body = unmarshal_request(
            schema_unmarshaler, oas_req, operation
        )
        if 'path' in parameters:
            params.update(parameters['path'])

        context.user = user
        context.parameters = parameters
        context.request_body = request_body


def _get_security_schemes(spec, base_module=''):
    security_schemes = spec.get_security_schemes()
    return security_schemes and {
        key: (
            security_scheme,
            import_string(
                security_scheme[extensions.IMPLEMENTATION],
                base_module=base_module,
            ),
        )
        for key, security_scheme in iteritems(security_schemes)
        if extensions.IMPLEMENTATION in security_scheme
    }
