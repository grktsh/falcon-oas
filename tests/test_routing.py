# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest

from falcon_oas.extensions import FALCON_OAS_IMPLEMENTOR
from falcon_oas.oas.spec import create_spec_from_dict
from falcon_oas.routing import generate_routes
from tests.helpers import yaml_load_dedent


class Resource(object):
    pass


@pytest.fixture
def spec_dict():
    return yaml_load_dedent(
        """\
        paths:
          /path1:
            {}: test_routing.Resource
          /path2:
            get:
              responses:
                default:
                  description: Success
        """.format(
            FALCON_OAS_IMPLEMENTOR
        )
    )


def test_generate_routes(spec_dict):
    spec = create_spec_from_dict(spec_dict)
    routes = list(generate_routes(spec, base_module='tests'))
    assert routes == [('/path1', Resource)]
