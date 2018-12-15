from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ..oas.exceptions import MissingMediaType
from ..oas.exceptions import ParametersError
from ..oas.exceptions import RequestBodyError
from ..oas.exceptions import UnmarshalError


class RequestUnmarshalMiddleware(object):
    def __init__(self, parameters, request_body):
        self.unmarshal_parameters = parameters.unmarshal
        self.unmarshal_request_body = request_body.unmarshal

    def process_resource(self, req, resp, resource, params):
        operation = req.context['oas._operation']
        if operation is None:
            return

        parameters_error = None
        request_body_error = None

        oas_req = req.context['oas._request']
        try:
            parameters = self.unmarshal_parameters(
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
                if oas_req.media_type is None:
                    raise MissingMediaType()

                request_body = self.unmarshal_request_body(
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
