# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import textwrap

import yaml


def yaml_load_dedent(text):
    return yaml.safe_load(textwrap.dedent(text))
