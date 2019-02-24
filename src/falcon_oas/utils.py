from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import functools
import importlib


def import_string(name, base_module=''):
    if base_module and not base_module.endswith('.'):
        base_module += '.'

    module_name, object_name = (base_module + name).rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, object_name)


class cached_property(object):
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func

    def __get__(self, instance, owner):
        if instance is None:  # pragma: no cover
            return self
        value = instance.__dict__[self.__name__] = self.func(instance)
        return value
