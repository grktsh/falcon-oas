from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ..oas.exceptions import UnmarshalError
from ..oas.parameters.unmarshalers import unmarshal_parameters
from ..oas.request_body import unmarshal_request_body


class RequestUnmarshalMiddleware(object):
    def __init__(self, schema_unmarshaler):
        self._schema_unmarshaler = schema_unmarshaler

    def process_resource(self, req, resp, resource, params):
        oas = req.context['oas']
        if not oas:
            return

        parameters, parameter_errors = unmarshal_parameters(
            self._schema_unmarshaler, oas.request, oas.operation['parameters']
        )
        if parameter_errors is None:
            oas.parameters = parameters
            if 'path' in parameters:
                params.update(parameters['path'])
        else:
            for error in parameter_errors:
                error.schema_path.appendleft('parameters')

        if 'requestBody' in oas.operation:
            request_body, request_body_errors = unmarshal_request_body(
                self._schema_unmarshaler,
                oas.request,
                oas.operation['requestBody'],
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
