# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import pytest
from falcon import testing


@pytest.fixture
def resource():
    return testing.SimpleTestResource()
