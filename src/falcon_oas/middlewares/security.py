from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import falcon
from six import iteritems

from .. import extensions
from ..utils import import_string

logger = logging.getLogger(__name__)


class SecurityMiddleware(object):
    def __init__(self, security_schemes):
        self._security_schemes = security_schemes

    def process_resource(self, req, resp, resource, params):
        oas = req.context['oas']
        if not oas:
            return

        if self._security_schemes and oas.operation['security']:
            # ``requirement`` is a alternative security requirement
            # object.  Only one of the security requirement objects
            # need to be satisfied to authorize a request.
            for requirement in oas.operation['security']:
                user = self._satisfy_requirement(oas.request, requirement)
                if user:
                    if user is not True:
                        oas.user = user
                    return

            logger.warning(
                'No security requirement was satisfied: %r',
                oas.operation['security'],
            )
            # TODO: distinguish unauthorized error from forbidden error
            raise falcon.HTTPForbidden()

    def _satisfy_requirement(self, oas_req, requirement):
        # All schemes MUST be satisfied for a request to be authorized.
        result = True
        for name, scopes in iteritems(requirement):
            user = self._satisfy_scheme(oas_req, name, scopes)
            if not user:
                return False
            if user is not True:
                result = user
        return result

    def _satisfy_scheme(self, oas_req, name, scopes):
        # Each name MUST correspond to a security scheme which is
        # declared in the Security Schemes under the Components Object,
        try:
            security_scheme, satisfy = self._security_schemes[name]
        except KeyError:
            # When ``extensions.IMPLEMENTATION`` is not specified,
            # KeyError is raised.
            return True

        if security_scheme['type'] == 'apiKey':
            location = security_scheme['in']
            name = security_scheme['name']
            value = getattr(oas_req, location).get(name)
            return satisfy(value, scopes, oas_req)

        logger.warning(
            'Unsupported security scheme type: %r', security_scheme['type']
        )
        return True


def get_security_schemes(spec, base_module=''):
    security_schemes = spec.get_security_schemes()
    return security_schemes and {
        key: (
            security_scheme,
            import_string(
                security_scheme[extensions.IMPLEMENTATION],
                base_module=base_module,
            ),
        )
        for key, security_scheme in iteritems(security_schemes)
        if extensions.IMPLEMENTATION in security_scheme
    }
