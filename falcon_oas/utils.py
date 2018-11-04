from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import importlib


def import_class_or_function(name, base_module=''):
    if base_module and not base_module.endswith('.'):
        base_module += '.'

    module_name, object_name = (base_module + name).rsplit(':', 1)
    module = importlib.import_module(module_name)
    return getattr(module, object_name)
