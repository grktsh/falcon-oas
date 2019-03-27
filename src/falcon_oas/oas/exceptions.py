from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class Error(Exception):
    pass


class UndocumentedMediaType(Error):
    pass


class ValidationError(Error):
    def __init__(self, errors):
        self.errors = errors


class UnmarshalError(Error):
    def __init__(self, parameter_errors=None, request_body_errors=None):
        self.parameter_errors = parameter_errors
        self.request_body_errors = request_body_errors

    def to_dict(self, obj_type=dict):
        obj = obj_type()

        if self.parameter_errors is not None:
            obj['parameters'] = [
                _error_to_dict(error, obj_type)
                for error in self.parameter_errors
            ]

        if self.request_body_errors is not None:
            obj['request_body'] = [
                _error_to_dict(error, obj_type)
                for error in self.request_body_errors
            ]

        return obj


def _error_to_dict(error, obj_type):
    obj = obj_type()
    obj['path'] = list(error.path)
    obj['validator'] = error.validator
    obj['message'] = error.message
    return obj
