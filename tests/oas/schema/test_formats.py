# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import base64
import datetime

import jsonschema
import pytest
import pytz

from falcon_oas.oas.schema.formats import default_formats
from falcon_oas.oas.schema.formats import Formats


@pytest.mark.parametrize(
    'name,value,expected',
    [
        ('int32', 0, None),
        ('int32', -2 ** 31, None),
        ('int32', 2 ** 31 - 1, None),
        ('int64', 0, None),
        ('int64', -2 ** 63, None),
        ('int64', 2 ** 63 - 1, None),
        ('byte', base64.b64encode(b'foo'), b'foo'),
        ('binary', '010203', b'\x01\x02\x03'),
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
def test_default_checker_success(name, value, expected):
    format_checker = default_formats.format_checker
    try:
        format_checker.check(value, name)
    except Exception as e:
        pytest.fail('Unexpected error: {}'.format(e))


@pytest.mark.parametrize(
    'name,value',
    [
        ('int32', -2 ** 31 - 1),
        ('int32', 2 ** 31),
        ('int64', -2 ** 63 - 1),
        ('int64', 2 ** 63),
        ('byte', 'xxx'),
        ('binary', 'xxx'),
        ('date', '2020/01/02'),
        ('date-time', '2020-01-02T03:04:05'),
        ('date-time', '2020/01/02T03:04:05Z'),
        ('uri', 'http'),
        ('uri', 'http://'),
        ('uri', 'example.com'),
        ('uri', 'example.com/path'),
    ],
)
def test_default_checker_error(name, value):
    format_checker = default_formats.format_checker

    with pytest.raises(jsonschema.FormatError):
        format_checker.check(value, name)


@pytest.mark.parametrize(
    'name,value,expected',
    [
        ('int32', 0, None),
        ('int32', -2 ** 31, None),
        ('int32', 2 ** 31 - 1, None),
        ('int64', 0, None),
        ('int64', -2 ** 63, None),
        ('int64', 2 ** 63 - 1, None),
        ('byte', base64.b64encode(b'foo'), b'foo'),
        ('binary', '010203', b'\x01\x02\x03'),
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
def test_default_modifier(name, value, expected):
    if expected is None:
        expected = value
    assert default_formats[name](value) == expected


def test_custom():
    formats = Formats()

    def create_date_parser(format):
        def parse_date(value):
            return datetime.datetime.strptime(value, format).date()

        return parse_date

    formats.register('date', 'string')(create_date_parser('%Y-%m-%d'))
    assert formats['date']('2020-01-02') == datetime.date(2020, 1, 2)
    pytest.raises(ValueError, formats['date'], '2020/01/02')

    formats.register('date', 'string')(create_date_parser('%Y/%m/%d'))
    assert formats['date']('2020/01/02') == datetime.date(2020, 1, 2)
    pytest.raises(ValueError, formats['date'], '2020-01-02')
