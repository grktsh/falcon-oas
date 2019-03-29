# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import pytest
import yaml


@pytest.fixture
def petstore_dict():
    spec_path = os.path.join(os.path.dirname(__file__), 'petstore.yaml')
    with open(spec_path) as f:
        return yaml.safe_load(f)
