# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from falcon_oas.utils import import_class_or_function

OBJECT = object()


def test_import_without_base_module():
    name = 'tests.test_utils:OBJECT'
    assert import_class_or_function(name) is OBJECT


def test_import_wit_base_module():
    name = 'test_utils:OBJECT'
    assert import_class_or_function(name, base_module='tests') is OBJECT


def test_import_wit_base_module_dot():
    name = 'test_utils:OBJECT'
    assert import_class_or_function(name, base_module='tests.') is OBJECT
