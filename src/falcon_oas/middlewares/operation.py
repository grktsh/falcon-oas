from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import falcon

from ..oas.exceptions import UndocumentedMediaType
from ..oas.request.models import Request
from ..utils import cached_property

logger = logging.getLogger(__name__)


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
    __slots__ = ('operation', 'request', 'user', 'parameters', 'request_body')

    def __init__(
        self, operation, request, user=None, parameters=None, request_body=None
    ):
        self.operation = operation
        self.request = request
        self.user = user
        self.parameters = parameters
        self.request_body = request_body


class OperationMiddleware(object):
    def __init__(self, spec):
        self._spec = spec

    def process_resource(self, req, resp, resource, params):
        oas_req = _RequestAdapter(req, params)

        try:
            operation = self._spec.get_operation(
                oas_req.uri_template, oas_req.method, oas_req.media_type
            )
        except UndocumentedMediaType:
            logger.warning(
                'Undocumented media type: %s %s (%s)',
                req.method,
                req.path,
                req.content_type,
            )
            raise falcon.HTTPBadRequest()

        req.context['oas'] = operation and _Context(operation, oas_req)
