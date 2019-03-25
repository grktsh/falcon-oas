from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ..oas.exceptions import UnmarshalError
from ..oas.parameters.unmarshalers import ParametersUnmarshaler
from ..oas.request_body import RequestBodyUnmarshaler


class RequestUnmarshalMiddleware(object):
    def __init__(self, schema_unmarshaler):
        self._unmarshal_parameters = ParametersUnmarshaler(
            schema_unmarshaler
        ).unmarshal
        self._unmarshal_request_body = RequestBodyUnmarshaler(
            schema_unmarshaler
        ).unmarshal

    def process_resource(self, req, resp, resource, params):
        oas = req.context['oas']
        if not oas:
            return

        parameters, parameter_errors = self._unmarshal_parameters(
            oas.request, oas.operation['parameters']
        )
        if parameter_errors is None:
            oas.parameters = parameters
            if 'path' in parameters:
                params.update(parameters['path'])
        else:
            for error in parameter_errors:
                error.schema_path.appendleft('parameters')

        if 'requestBody' in oas.operation:
            request_body, request_body_errors = self._unmarshal_request_body(
                oas.request, oas.operation['requestBody']
            )
            if request_body_errors is None:
                oas.request_body = request_body
            else:
                for error in request_body_errors:
                    error.schema_path.appendleft('requestBody')
        else:
            request_body_errors = None

        if parameter_errors or request_body_errors:
            raise UnmarshalError(parameter_errors, request_body_errors)
