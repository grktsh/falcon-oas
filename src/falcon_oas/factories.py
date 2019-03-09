from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon

from .middlewares.operation import OperationMiddleware
from .middlewares.request_unmarshal import RequestUnmarshalMiddleware
from .middlewares.security import get_security_schemes
from .middlewares.security import SecurityMiddleware
from .oas.exceptions import UnmarshalError
from .oas.schema.unmarshalers import SchemaUnmarshaler
from .oas.spec import create_spec_from_dict
from .problems import http_error_handler
from .problems import serialize_problem
from .problems import unmarshal_error_handler
from .routing import generate_routes


class OAS(object):
    def __init__(
        self,
        spec_dict,
        parsers=None,
        base_module='',
        base_path=None,
        api_factory=falcon.API,
        problems=True,
    ):
        self.spec = create_spec_from_dict(spec_dict, base_path=base_path)
        self.parsers = parsers
        self.base_module = base_module
        self.api_factory = api_factory
        self.problems = problems

    def create_api(self, **options):
        if 'middleware' not in options:
            options['middleware'] = self.middlewares

        return self.setup(self.api_factory(**options))

    @property
    def middlewares(self):
        security_schemes = get_security_schemes(
            self.spec, base_module=self.base_module
        )
        schema_unmarshaler = SchemaUnmarshaler(parsers=self.parsers)
        return [
            OperationMiddleware(self.spec),
            SecurityMiddleware(security_schemes),
            RequestUnmarshalMiddleware(schema_unmarshaler),
        ]

    def setup(self, api):
        api.req_options.auto_parse_qs_csv = False

        if self.problems:
            api.add_error_handler(falcon.HTTPError, http_error_handler)
            api.add_error_handler(UnmarshalError, unmarshal_error_handler)
            api.set_error_serializer(serialize_problem)

        for uri_template, resource_class in generate_routes(
            self.spec, base_module=self.base_module
        ):
            api.add_route(uri_template, resource_class())

        return api
