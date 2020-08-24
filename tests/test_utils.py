# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from falcon_oas.utils import import_string

OBJECT = object()


def test_import_string_without_base_module():
    name = 'tests.test_utils.OBJECT'
    assert import_string(name) is OBJECT


def test_import_string_with_base_module():
    name = 'test_utils.OBJECT'
    assert import_string(name, base_module='tests') is OBJECT


def test_import_string_with_base_module_dot():
    name = 'test_utils.OBJECT'
    assert import_string(name, base_module='tests.') is OBJECT


def test_import_string_with_callable():
    def func():
        return

    assert import_string(func) is func
