from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ..oas.exceptions import MissingMediaType
from ..oas.exceptions import ParametersError
from ..oas.exceptions import RequestBodyError
from ..oas.exceptions import UnmarshalError


class FalconOASRequest(object):
    def __init__(self, req, params):
        self.req = req
        self.params = params

    @property
    def full_path(self):
        return self.req.uri_template

    @property
    def method(self):
        return self.req.method.lower()

    @property
    def parameters(self):
        return {
            'query': self.req.params,
            'header': self.req.headers,
            'path': self.params,
            'cookie': self.req.cookies,
        }

    @property
    def media_type(self):
        content_type = self.req.content_type
        return content_type and content_type.split(';', 1)[0]

    def get_media(self):
        return self.req.media


class RequestUnmarshaler(object):
    def __init__(self, spec, parameters, request_body):
        self.spec = spec
        self.unmarshal_parameters = parameters.unmarshal
        self.unmarshal_request_body = request_body.unmarshal

    def process_resource(self, req, resp, resource, params):
        oas_req = FalconOASRequest(req, params)

        operation = self.spec.get_operation(oas_req.full_path, oas_req.method)
        if operation is None:
            # Undocumented request
            return

        parameters_error = None
        request_body_error = None

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
