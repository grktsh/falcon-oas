from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon

from .middlewares import Middleware
from .oas.exceptions import SecurityError
from .oas.exceptions import UndocumentedMediaType
from .oas.exceptions import UnmarshalError
from .oas.spec import create_spec_from_dict
from .problems import http_error_handler
from .problems import security_error_handler
from .problems import serialize_problem
from .problems import undocumented_media_type_handler
from .problems import unmarshal_error_handler
from .routing import generate_routes


class OAS(object):
    def __init__(
        self,
        spec_dict,
        formats=None,
        base_module='',
        api_factory=falcon.API,
        problems=True,
    ):
        self.spec = create_spec_from_dict(spec_dict)
        self.formats = formats
        self.base_module = base_module
        self.api_factory = api_factory
        self.problems = problems

    def create_api(self, **options):
        if 'middleware' not in options:
            options['middleware'] = self.middleware

        return self.setup(self.api_factory(**options))

    @property
    def middleware(self):
        return Middleware(
            self.spec, formats=self.formats, base_module=self.base_module
        )

    def setup(self, api):
        api.req_options.auto_parse_qs_csv = False

        api.add_error_handler(
            UndocumentedMediaType, undocumented_media_type_handler
        )
        api.add_error_handler(SecurityError, security_error_handler)
        api.add_error_handler(UnmarshalError, unmarshal_error_handler)

        if self.problems:
            api.add_error_handler(falcon.HTTPError, http_error_handler)
            api.set_error_serializer(serialize_problem)

        for uri_template, resource_class in generate_routes(
            self.spec, base_module=self.base_module
        ):
            api.add_route(uri_template, resource_class())

        return api
