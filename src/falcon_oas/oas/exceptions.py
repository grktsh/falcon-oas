from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class _Error(Exception):
    pass


class UndocumentedRequest(_Error):
    pass


class UndocumentedMediaType(UndocumentedRequest):
    pass


class ValidationError(_Error):
    def __init__(self, errors):
        super(ValidationError, self).__init__()
        self.errors = errors


class UnmarshalError(_Error):
    def __init__(self, parameters_error=None, request_body_error=None):
        super(UnmarshalError, self).__init__()
        self.parameters_error = parameters_error
        self.request_body_error = request_body_error

    def to_dict(self, obj_type=dict):
        obj = obj_type()
        if self.parameters_error is not None:
            obj.update(self.parameters_error.to_dict(obj_type=obj_type))
        if self.request_body_error is not None:
            obj.update(self.request_body_error.to_dict(obj_type=obj_type))
        return obj


class ParametersError(_Error):
    def __init__(self, errors):
        super(ParametersError, self).__init__()
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


class ParameterError(_Error):
    def __init__(self, name, location, errors):
        super(ParameterError, self).__init__()
        self.name = name
        self.location = location
        self.errors = errors

    def to_dict(self, obj_type=dict):
        obj = obj_type()
        obj[self.location] = [
            self._error_to_dict(error, obj_type) for error in self.errors
        ]
        return obj

    def _error_to_dict(self, error, obj_type):
        obj = obj_type()
        obj['name'] = self.name
        obj.update(_error_to_dict(error, obj_type))
        return obj


class RequestBodyError(_Error):
    def __init__(self, errors):
        super(RequestBodyError, self).__init__()
        self.errors = errors

    def to_dict(self, obj_type=dict):
        obj = obj_type()
        obj['request_body'] = [
            _error_to_dict(error, obj_type) for error in self.errors
        ]
        return obj


class _ValidationError(object):
    path = None
    validator = None
    message = None


class MissingParameter(ParameterError):
    def __init__(self, name, location):
        class _MissingParameter(_ValidationError):
            validator = 'required'
            message = 'parameter is required'

        errors = [_MissingParameter()]
        super(MissingParameter, self).__init__(name, location, errors)


class MissingRequestBody(RequestBodyError):
    def __init__(self, media_type):
        class _MissingRequestBody(_ValidationError):
            validator = 'required'
            message = 'request body is required'

        super(MissingRequestBody, self).__init__([_MissingRequestBody()])
        self.media_type = media_type


def _error_to_dict(error, obj_type):
    obj = obj_type()
    if error.path:
        obj['path'] = '.'.join(str(x) for x in error.path)
    obj['validator'] = error.validator
    obj['message'] = error.message
    return obj
