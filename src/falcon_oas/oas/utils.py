from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools


class cached_property(object):
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:  # pragma: no cover
            return self
        value = instance.__dict__[self.__name__] = self.func(instance)
        return value
