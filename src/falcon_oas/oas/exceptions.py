from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class Error(Exception):
    pass


class UndocumentedRequest(Error):
    pass


class UndocumentedMediaType(UndocumentedRequest):
    pass


class ValidationError(Error):
    def __init__(self, errors):
        self.errors = errors


class UnmarshalError(Error):
    def __init__(self, parameters_error=None, request_body_error=None):
        self.parameters_error = parameters_error
        self.request_body_error = request_body_error

    def to_dict(self, obj_type=dict):
        obj = obj_type()
        if self.parameters_error is not None:
            obj.update(self.parameters_error.to_dict(obj_type=obj_type))
        if self.request_body_error is not None:
            obj.update(self.request_body_error.to_dict(obj_type=obj_type))
        return obj


class ParametersError(Error):
    def __init__(self, errors):
        self.errors = errors

    def to_dict(self, obj_type=dict):
        parameters = obj_type()
        for error in self.errors:
            error_dict = error.to_dict(obj_type=obj_type)
            if error.location not in parameters:
                parameters.update(error_dict)
            else:
                parameters[error.location].extend(error_dict[error.location])
        obj = obj_type()
        obj['parameters'] = parameters
        return obj


class ParameterError(Error):
    def __init__(self, name, location, errors):
        self.name = name
        self.location = location
        self.errors = errors

    def to_dict(self, obj_type=dict):
        obj = obj_type()
        obj[self.location] = [
            _error_to_dict(error, obj_type, name=self.name)
            for error in self.errors
        ]
        return obj


class RequestBodyError(Error):
    def __init__(self, errors):
        self.errors = errors

    def to_dict(self, obj_type=dict):
        obj = obj_type()
        obj['request_body'] = [
            _error_to_dict(error, obj_type) for error in self.errors
        ]
        return obj


class _Missing(object):
    path = []
    validator = 'required'

    def __init__(self, name):
        self.message = name + ' is required'


class MissingParameter(ParameterError):
    errors = [_Missing('parameter')]

    def __init__(self, name, location):
        self.name = name
        self.location = location


class MissingRequestBody(RequestBodyError):
    errors = [_Missing('request body')]

    def __init__(self, media_type):
        self.media_type = media_type


def _error_to_dict(error, obj_type, **kwargs):
    obj = obj_type()
    obj['path'] = list(error.path)
    obj['validator'] = error.validator
    obj['message'] = error.message
    obj.update(**kwargs)
    return obj
