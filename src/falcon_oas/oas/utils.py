from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import json


def pretty_json(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)
