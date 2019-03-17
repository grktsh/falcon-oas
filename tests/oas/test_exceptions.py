# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import jsonschema

from falcon_oas.oas.exceptions import UnmarshalError


def test_unmarshal_error():
    error = UnmarshalError(
        [
            jsonschema.ValidationError(
                "'p1' is a required in 'query' parameter",
                validator='required',
                path=('path', 'p1'),
            ),
            jsonschema.ValidationError(
                "'123' is not of type 'integer'",
                validator='type',
                path=('query', 'p2'),
            ),
        ],
        [
            jsonschema.ValidationError(
                'Request body is required', validator='required'
            )
        ],
    )
    assert error.to_dict() == {
        'parameters': {
            'path': [
                {
                    'name': 'p1',
                    'path': ['path', 'p1'],
                    'validator': 'required',
                    'message': "'p1' is a required in 'query' parameter",
                }
            ],
            'query': [
                {
                    'name': 'p2',
                    'path': ['query', 'p2'],
                    'validator': 'type',
                    'message': "'123' is not of type 'integer'",
                }
            ],
        },
        'request_body': [
            {
                'path': [],
                'validator': 'required',
                'message': 'Request body is required',
            }
        ],
    }


def test_no_unmarshal_error():
    error = UnmarshalError()
    assert error.to_dict() == {}
