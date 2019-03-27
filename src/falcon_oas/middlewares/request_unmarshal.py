from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ..oas.request.unmarshalers import unmarshal_request


class RequestUnmarshalMiddleware(object):
    def __init__(self, schema_unmarshaler):
        self._schema_unmarshaler = schema_unmarshaler

    def process_resource(self, req, resp, resource, params):
        oas = req.context['oas']
        if not oas:
            return

        oas.parameters, oas.request_body = unmarshal_request(
            self._schema_unmarshaler, oas.request, oas.operation
        )
        if 'path' in oas.parameters:
            params.update(oas.parameters['path'])
