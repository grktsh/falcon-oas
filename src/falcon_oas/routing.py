from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import iteritems

from .extensions import X_FALCON_RESOURCE
from .utils import import_string


def generate_routes(spec, base_module=''):
    for path, path_item in iteritems(spec.spec_dict['paths']):
        try:
            resource_name = path_item[X_FALCON_RESOURCE]
        except KeyError:
            pass
        else:
            resource_class = import_string(
                resource_name, base_module=base_module
            )
            yield spec.base_path + path, resource_class()
