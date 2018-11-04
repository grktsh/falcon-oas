# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from falcon import testing

from falcon_oas.factories import create_api


class Resource(object):
    def on_get(self, req, resp):
        resp.media = {'x': 2}


def test_create_api():
    api = create_api(
        {
            'paths': {
                '/path': {
                    'x-falcon-resource': 'test_factories:Resource',
                    'get': {},
                }
            }
        },
        base_module='tests',
    )
    client = testing.TestClient(api)
    result = client.simulate_get('/path')
    assert result.json == {'x': 2}
