from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import falcon
from six import iteritems

from ..extensions import FALCON_OAS_IMPLEMENTOR
from ..utils import import_string

logger = logging.getLogger(__name__)


class SecurityMiddleware(object):
    def __init__(self, security_schemes):
        self.security_schemes = security_schemes

    def process_resource(self, req, resp, resource, params):
        operation = req.context['oas.operation']
        if operation is None:
            return

        if self.security_schemes and operation['security']:
            oas_req = req.context['oas.request']

            for requirement in operation['security']:
                user = self._satisfy_requirement(oas_req, requirement)
                if user:
                    if user is not True:
                        req.context['oas.user'] = user
                    return

            logger.warning(
                'No security requirement was satisfied: %r',
                operation['security'],
            )
            # TODO: distinguish unauthorized error from forbidden error
            raise falcon.HTTPForbidden()

    def _satisfy_requirement(self, oas_req, requirement):
        result = True
        for key, scopes in iteritems(requirement):
            user = self._satisfy_scheme(oas_req, key, scopes)
            if not user:
                return False
            if user is not True:
                result = user
        return result

    def _satisfy_scheme(self, oas_req, key, scopes):
        try:
            security_scheme, satisfy = self.security_schemes[key]
        except KeyError:
            return True

        if security_scheme['type'] == 'apiKey':
            location = security_scheme['in']
            name = security_scheme['name']
            value = oas_req.parameters[location].get(name)
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
                security_scheme[FALCON_OAS_IMPLEMENTOR],
                base_module=base_module,
            ),
        )
        for key, security_scheme in iteritems(security_schemes)
        if FALCON_OAS_IMPLEMENTOR in security_scheme
    }
