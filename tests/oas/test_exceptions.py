# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import jsonschema

from falcon_oas.oas.exceptions import MissingParameter
from falcon_oas.oas.exceptions import MissingRequestBody
from falcon_oas.oas.exceptions import ParameterError
from falcon_oas.oas.exceptions import ParametersError
from falcon_oas.oas.exceptions import RequestBodyError
from falcon_oas.oas.exceptions import UnmarshalError


def test_unmarshal_error():
    error = UnmarshalError(
        ParametersError([MissingParameter('p1', 'query')]),
        MissingRequestBody('application/json'),
    )
    assert error.to_dict() == {
        'parameters': {
            'query': [
                {
                    'name': 'p1',
                    'validator': 'required',
                    'message': 'parameter is required',
                }
            ]
        },
        'request_body': [
            {'validator': 'required', 'message': 'request body is required'}
        ],
    }


def test_no_unmarshal_error():
    error = UnmarshalError(None, None)
    assert error.to_dict() == {}


def test_parameters_error():
    errors = [
        ParameterError(
            'p1',
            'query',
            errors=[
                jsonschema.ValidationError(
                    "u'123' is not of type u'integer'", validator='type'
                ),
                jsonschema.ValidationError(
                    "u'2018/01/02' is not a u'date'",
                    validator='format',
                    path=['p1', 0, 'p2'],
                ),
            ],
        ),
        MissingParameter('p2', 'query'),
    ]
    assert ParametersError(errors).to_dict() == {
        'parameters': {
            'query': [
                {
                    'name': 'p1',
                    'validator': 'type',
                    'message': "u'123' is not of type u'integer'",
                },
                {
                    'name': 'p1',
                    'path': 'p1.0.p2',
                    'validator': 'format',
                    'message': "u'2018/01/02' is not a u'date'",
                },
                {
                    'name': 'p2',
                    'validator': 'required',
                    'message': 'parameter is required',
                },
            ]
        }
    }


def test_request_body_validation_errors():
    errors = [
        jsonschema.ValidationError(
            "u'123' is not of type u'integer'", validator='type'
        ),
        jsonschema.ValidationError(
            "u'2018/01/02' is not a u'date'",
            validator='format',
            path=['p1', 'p2'],
        ),
    ]
    assert RequestBodyError(errors).to_dict() == {
        'request_body': [
            {
                'validator': 'type',
                'message': "u'123' is not of type u'integer'",
            },
            {
                'path': 'p1.p2',
                'validator': 'format',
                'message': "u'2018/01/02' is not a u'date'",
            },
        ]
    }


def test_request_body_missing_request_body():
    error = MissingRequestBody(str('application/json'))
    assert error.to_dict() == {
        'request_body': [
            {'validator': 'required', 'message': 'request body is required'}
        ]
    }
