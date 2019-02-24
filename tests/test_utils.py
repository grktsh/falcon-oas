# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from falcon_oas.utils import cached_property
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


def test_cached_property():
    class C(object):
        def __init__(self):
            self._called = 0

        @cached_property
        def called(self):
            """A docstring"""
            self._called += 1
            return self._called

    obj = C()
    assert obj.called == 1
    assert obj.called == 1
