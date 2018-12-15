from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from falcon import CaseInsensitiveDict

from ..oas.exceptions import UndocumentedRequest


class _RequestAdapter(object):
    def __init__(self, req, params):
        self.req = req
        self.params = params

    @property
    def uri_template(self):
        return self.req.uri_template

    @property
    def method(self):
        return self.req.method.lower()

    @property
    def parameters(self):
        return {
            'query': self.req.params,
            'header': CaseInsensitiveDict(self.req.headers),
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
        except UndocumentedRequest:
            operation = None

        req.context['oas._operation'] = operation
        req.context['oas._request'] = oas_req
