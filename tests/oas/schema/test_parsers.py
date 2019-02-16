# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime

import pytest
import pytz

from falcon_oas.oas.schema.parsers import DEFAULT_PARSERS


@pytest.mark.parametrize(
    'name,value,expected',
    [
        ('int32', '0', 0),
        ('int32', str(-2 ** 31), -2 ** 31),
        ('int32', str(2 ** 31 - 1), 2 ** 31 - 1),
        ('int64', '0', 0),
        ('int64', str(-2 ** 63), -2 ** 63),
        ('int64', str(2 ** 63 - 1), 2 ** 63 - 1),
        ('date', '2020-01-02', datetime.date(2020, 1, 2)),
        (
            'date-time',
            '2020-01-02T03:04:05Z',
            datetime.datetime(2020, 1, 2, 3, 4, 5, tzinfo=pytz.utc),
        ),
        ('uri', 'http://example.com', None),
        ('uri', 'https://example.com', None),
        ('uri', 'https://example.com/', None),
        ('uri', 'https://example.com/path', None),
        ('uri', 'https://example.com/path?query#segment', None),
    ],
)
def test_success(name, value, expected):
    if expected is None:
        expected = value
    assert DEFAULT_PARSERS[name](value) == expected


@pytest.mark.parametrize(
    'name,value',
    [
        ('int32', 'x'),
        ('int32', str(-2 ** 31 - 1)),
        ('int32', str(2 ** 31)),
        ('int64', 'x'),
        ('int64', str(-2 ** 63 - 1)),
        ('int64', str(2 ** 63)),
        ('date', '2020/01/02'),
        ('date-time', '2020-01-02T03:04:05'),
        ('date-time', '2020/01/02T03:04:05Z'),
        ('uri', 'http'),
        ('uri', 'http://'),
        ('uri', 'example.com'),
        ('uri', 'example.com/path'),
    ],
)
def test_error(name, value):
    pytest.raises(ValueError, DEFAULT_PARSERS[name], value)
