from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ..oas.exceptions import ParametersError
from ..oas.exceptions import RequestBodyError
from ..oas.exceptions import UnmarshalError
from ..oas.parameters.unmarshalers import ParametersUnmarshaler
from ..oas.request_body import RequestBodyUnmarshaler


class RequestUnmarshalMiddleware(object):
    def __init__(self, schema_unmarshaler):
        self.parameters_unmarshaler = ParametersUnmarshaler(schema_unmarshaler)
        self.request_body_unmarshaler = RequestBodyUnmarshaler(
            schema_unmarshaler
        )

    def process_resource(self, req, resp, resource, params):
        operation = req.context['oas.operation']
        if operation is None:
            return

        parameters_error = None
        request_body_error = None

        oas_req = req.context['oas.request']
        try:
            parameters = self.parameters_unmarshaler.unmarshal(
                oas_req.parameters, operation['parameters']
            )
        except ParametersError as e:
            parameters_error = e
        else:
            req.context['oas.parameters'] = parameters
            if 'path' in parameters:
                params.update(parameters['path'])

        if 'requestBody' in operation:
            try:
                request_body = self.request_body_unmarshaler.unmarshal(
                    oas_req.get_media,
                    oas_req.media_type,
                    operation['requestBody'],
                )
            except RequestBodyError as e:
                request_body_error = e
            else:
                req.context['oas.request_body'] = request_body

        if parameters_error or request_body_error:
            raise UnmarshalError(parameters_error, request_body_error)
