from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ..exceptions import UnmarshalError
from ..parameters.unmarshalers import unmarshal_parameters
from ..request_body import unmarshal_request_body


def unmarshal_request(schema_unmarshaler, request, operation):
    parameters, parameter_errors = unmarshal_parameters(
        schema_unmarshaler, request, operation['parameters']
    )
    if parameter_errors:
        for error in parameter_errors:
            error.schema_path.appendleft('parameters')

    if 'requestBody' in operation:
        request_body, request_body_errors = unmarshal_request_body(
            schema_unmarshaler, request, operation['requestBody']
        )
        if request_body_errors:
            for error in request_body_errors:
                error.schema_path.appendleft('requestBody')
    else:
        request_body = None
        request_body_errors = None

    if parameter_errors or request_body_errors:
        raise UnmarshalError(parameter_errors, request_body_errors)

    return parameters, request_body
