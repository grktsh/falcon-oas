from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import copy

import jsonref

try:
    from functools import lru_cache
except ImportError:  # pragma: no cover
    from functools32 import lru_cache
from six.moves.urllib_parse import urlparse

from .exceptions import UndocumentedMediaType


def create_spec_from_dict(spec_dict):
    deref_spec_dict = jsonref.JsonRef.replace_refs(spec_dict)
    return Spec(copy.deepcopy(deref_spec_dict))


class Spec(object):
    def __init__(self, spec_dict):
        self.data = spec_dict
        self.base_path = _get_base_path(spec_dict)
        self._base_security = _get_security(spec_dict)

    @lru_cache(maxsize=None)
    def get_operation(self, uri_template, method, media_type):
        if not uri_template.startswith(self.base_path):
            return None

        path = uri_template[len(self.base_path) :]
        try:
            # ``paths`` is required in OpenAPI Object.
            path_item = self.data['paths'][path]
            operation = path_item[method]
        except KeyError:
            return None

        if 'requestBody' in operation:
            # TODO: Support media type range
            # ``content`` is required in Request Body Object.
            if media_type not in operation['requestBody']['content']:
                raise UndocumentedMediaType()

        result = operation.copy()
        result['parameters'] = list(self._iter_parameters(result, path_item))
        # ``security`` of Operation Object overrides any declared
        # top-level ``security``.
        result['security'] = _get_security(
            result, base_security=self._base_security
        )
        return result

    def get_security_schemes(self):
        try:
            return self.data['components']['securitySchemes']
        except KeyError:
            return None

    def _iter_parameters(self, operation, path_item):
        """Iterate parameters of Operation Object and Path Item Object.

        Operation Object:

            If a parameter is already defined at the Path Item, the new
            definition will override it but can never remove it.

        Path Item Object:

            These parameters can be overridden at the operation level,
            but cannot be removed.
        """
        seen = set()
        for spec_dict in (operation, path_item):
            if 'parameters' not in spec_dict:
                continue
            for parameter_spec_dict in spec_dict['parameters']:
                # A unique parameter is defined by a combination of a
                # ``in`` and ``name``.
                key = (parameter_spec_dict['in'], parameter_spec_dict['name'])
                if key in seen:
                    continue
                seen.add(key)
                yield parameter_spec_dict

    def __getitem__(self, key):
        return self.data[key]


def _get_base_path(spec_dict):
    try:
        server = spec_dict['servers'][0]
    except (KeyError, IndexError):
        return ''
    else:
        # ``url`` is required in Server Object.
        return urlparse(server['url']).path.rstrip('/')


def _get_security(spec_dict, base_security=None):
    return spec_dict.get('security', base_security)
