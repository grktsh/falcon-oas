# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import base64
import datetime

import pytest
import pytz

from falcon_oas.oas.schema.formats import DEFAULT_FORMATS


@pytest.mark.parametrize(
    'schema_type,name,value,expected',
    [
        ('integer', 'int32', 0, None),
        ('integer', 'int32', -2 ** 31, None),
        ('integer', 'int32', 2 ** 31 - 1, None),
        ('integer', 'int64', 0, None),
        ('integer', 'int64', -2 ** 63, None),
        ('integer', 'int64', 2 ** 63 - 1, None),
        ('string', 'byte', base64.b64encode(b'foo'), b'foo'),
        ('string', 'binary', '010203', b'\x01\x02\x03'),
        ('string', 'date', '2020-01-02', datetime.date(2020, 1, 2)),
        (
            'string',
            'date-time',
            '2020-01-02T03:04:05Z',
            datetime.datetime(2020, 1, 2, 3, 4, 5, tzinfo=pytz.utc),
        ),
        ('string', 'uri', 'http://example.com', None),
        ('string', 'uri', 'https://example.com', None),
        ('string', 'uri', 'https://example.com/', None),
        ('string', 'uri', 'https://example.com/path', None),
        ('string', 'uri', 'https://example.com/path?query#segment', None),
    ],
)
def test_success(schema_type, name, value, expected):
    if expected is None:
        expected = value
    assert DEFAULT_FORMATS[schema_type][name](value) == expected


@pytest.mark.parametrize(
    'schema_type,name,value',
    [
        ('integer', 'int32', -2 ** 31 - 1),
        ('integer', 'int32', 2 ** 31),
        ('integer', 'int64', -2 ** 63 - 1),
        ('integer', 'int64', 2 ** 63),
        ('string', 'byte', 'xxx'),
        ('string', 'binary', 'xxx'),
        ('string', 'date', '2020/01/02'),
        ('string', 'date-time', '2020-01-02T03:04:05'),
        ('string', 'date-time', '2020/01/02T03:04:05Z'),
        ('string', 'uri', 'http'),
        ('string', 'uri', 'http://'),
        ('string', 'uri', 'example.com'),
        ('string', 'uri', 'example.com/path'),
    ],
)
def test_error(schema_type, name, value):
    pytest.raises(ValueError, DEFAULT_FORMATS[schema_type][name], value)
