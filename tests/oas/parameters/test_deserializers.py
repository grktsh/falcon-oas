from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from falcon_oas.oas.parameters.deserializers import deserialize_parameter


@pytest.mark.parametrize(
    'value,schema_type,expected',
    [
        ('2', 'integer', 2),
        ('2.3', 'number', 2.3),
        ('2', 'number', 2.0),
        ('1', 'boolean', True),
        ('0', 'boolean', False),
        ('true', 'boolean', True),
        ('false', 'boolean', False),
        ('t', 'boolean', True),
        ('f', 'boolean', False),
        ('yes', 'boolean', True),
        ('no', 'boolean', False),
        ('x', 'string', 'x'),
    ],
)
def test_deserialize_parameter(value, schema_type, expected):
    assert deserialize_parameter(value, {'type': schema_type}) == expected


@pytest.mark.parametrize(
    'value,schema_type,expected',
    [
        ('x', 'integer', 'x'),
        ('2.3', 'integer', '2.3'),
        ('x', 'number', 'x'),
        ('2', 'boolean', '2'),
        ('x', 'boolean', 'x'),
        ('{}', 'object', '{}'),  # Unsupported
        ('[]', 'array', '[]'),  # Unsupported
    ],
)
def test_deserialize_parameter_errors(value, schema_type, expected):
    assert deserialize_parameter(value, {'type': schema_type}) == expected
