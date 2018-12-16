from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from jsonschema import RefResolver
from six import iteritems

try:
    from functools import lru_cache
except ImportError:  # pragma: no cover
    from functools32 import lru_cache
from six.moves.urllib_parse import urlparse

from .exceptions import UndocumentedRequest, UndocumentedMediaType

DEFAULT_SERVER = {'url': '/'}


def create_spec_from_dict(spec_dict, base_path=None):
    return Spec(spec_dict, base_path=base_path)


class Spec(object):
    def __init__(self, spec_dict, base_path=None):
        self.spec_dict = spec_dict
        self.resolver = RefResolver.from_schema(spec_dict)
        self.base_path = (
            base_path if base_path is not None else get_base_path(spec_dict)
        )
        self._base_security = get_security(spec_dict)

    def deref(self, schema):
        while '$ref' in schema:
            _, schema = self.resolver.resolve(schema['$ref'])
        return schema

    @lru_cache(maxsize=None)
    def get_operation(self, uri_template, method, media_type):
        if not uri_template.startswith(self.base_path):
            raise UndocumentedRequest()

        path = uri_template[len(self.base_path) :]
        try:
            path_item = self.deref(self.spec_dict['paths'][path])
            operation = path_item[method]
        except KeyError:
            raise UndocumentedRequest()

        result = operation.copy()
        result['parameters'] = list(
            self._iter_parameters(path_item, operation)
        )
        try:
            result['requestBody'] = self._deref_request_body(
                operation, media_type
            )
        except KeyError:
            pass
        result['security'] = get_security(
            result, base_security=self._base_security
        )
        return result

    def get_security_schemes(self):
        try:
            security_schemes = self.spec_dict['components']['securitySchemes']
        except KeyError:
            return None
        else:
            return {
                key: self.deref(security_scheme)
                for key, security_scheme in iteritems(security_schemes)
            }

    def _iter_parameters(self, path_item, operation):
        seen = set()
        for spec_dict in (operation, path_item):
            if 'parameters' not in spec_dict:
                continue
            for parameter_spec_dict in spec_dict['parameters']:
                parameter_spec_dict = self.deref(parameter_spec_dict)
                key = (parameter_spec_dict['in'], parameter_spec_dict['name'])
                if key in seen:
                    continue
                seen.add(key)
                try:
                    schema = parameter_spec_dict['schema']
                except KeyError:
                    pass
                else:
                    parameter_spec_dict['schema'] = self.deref(schema)
                yield parameter_spec_dict

    def _deref_request_body(self, operation, media_type):
        result = self.deref(operation['requestBody'])
        try:
            # TODO: Support media type range
            media_type_spec_dict = result['content'][media_type]
        except KeyError:
            raise UndocumentedMediaType()
        try:
            schema = media_type_spec_dict['schema']
        except KeyError:
            pass
        else:
            media_type_spec_dict['schema'] = self.deref(schema)
        return result


def get_base_path(spec_dict):
    try:
        server = spec_dict['servers'][0]
    except (KeyError, IndexError):
        server = DEFAULT_SERVER
    return urlparse(server['url']).path.rstrip('/')


def get_security(spec_dict, base_security=None):
    try:
        return spec_dict['security']
    except KeyError:
        return base_security
