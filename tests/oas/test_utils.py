# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from falcon_oas.oas.utils import cached_property


def test_cached_property():
    class C(object):
        def __init__(self):
            self._called = 0

        @cached_property
        def called(self):
            self._called += 1
            return self._called

    obj = C()
    assert obj.called == 1
    assert obj.called == 1
