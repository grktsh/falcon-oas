# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from oas import create_spec_from_dict

from falcon_oas import extensions
from falcon_oas.routing import generate_routes


class Resource(object):
    pass


def test_generate_routes(petstore_dict):
    path_item = petstore_dict['paths']['/v1/pets']
    path_item[extensions.IMPLEMENTATION] = 'test_routing.Resource'

    spec = create_spec_from_dict(petstore_dict)
    routes = list(generate_routes(spec, base_module='tests'))
    assert routes == [('/api/v1/pets', Resource)]
