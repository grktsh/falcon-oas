from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import falcon

from ..oas.exceptions import UndocumentedMediaType
from ..oas.exceptions import UndocumentedRequest
from ..oas.request import Request
from ..utils import cached_property

logger = logging.getLogger(__name__)


class _Indexer(object):
    def __init__(self, getter):
        self.getter = getter

    def __getitem__(self, key):
        try:
            return self.getter(key, required=True)
        except falcon.HTTPBadRequest:
            raise KeyError(key)

    def get(self, key, default=None):
        return self.getter(key, default=default)


class _RequestAdapter(Request):
    def __init__(self, req, params):
        self.req = req
        self.params = params

    @property
    def uri_template(self):
        return self.req.uri_template

    @property
    def method(self):
        return self.req.method.lower()

    @cached_property
    def parameters(self):
        return {
            'query': self.req.params,
            'header': _Indexer(self.req.get_header),
            'path': self.params,
            'cookie': self.req.cookies,
        }

    @property
    def media_type(self):
        content_type = self.req.content_type
        return content_type and content_type.split(';', 1)[0]

    def get_media(self):
        return self.req.media


class OperationMiddleware(object):
    def __init__(self, spec):
        self.spec = spec

    def process_resource(self, req, resp, resource, params):
        oas_req = _RequestAdapter(req, params)

        try:
            operation = self.spec.get_operation(
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
        except UndocumentedRequest:
            logger.warning(
                'Undocumented request: %s %s (%s)',
                req.method,
                req.path,
                req.content_type,
            )
            operation = None

        req.context['oas.operation'] = operation
        req.context['oas.request'] = oas_req
