from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
from six import iteritems

from ..extensions import X_USER_LOADER
from ..utils import import_string


class SecurityMiddleware(object):
    def __init__(self, security_schemes):
        self.security_schemes = security_schemes

    def process_resource(self, req, resp, resource, params):
        operation = req.context['oas._operation']
        if operation is None:
            return

        if operation['security']:
            oas_req = req.context['oas._request']

            for requirement in operation['security']:
                user = self._satisfy_requirement(
                    oas_req.parameters, requirement
                )
                if user:
                    if user is not True:
                        req.context['oas.user'] = user
                    return

            # TODO: distinguish unauthorized error from forbidden error
            raise falcon.HTTPForbidden()

    def _satisfy_requirement(self, parameters, requirement):
        result = True
        for key, scopes in iteritems(requirement):
            user = self._satisfy_scheme(parameters, key, scopes)
            if not user:
                return False
            if user is not True:
                result = user
        return result

    def _satisfy_scheme(self, parameters, key, scopes):
        try:
            security_scheme, user_loader = self.security_schemes[key]
        except KeyError:
            return True

        if security_scheme['type'] == 'apiKey':
            location = security_scheme['in']
            name = security_scheme['name']
            try:
                value = parameters[location][name]
            except KeyError:
                return False
            return user_loader(value)
        # Unsupported yet
        return True


def get_security_schemes(spec_dict, base_module=''):
    try:
        security_schemes = spec_dict['components']['securitySchemes']
    except KeyError:
        return None
    else:
        return {
            key: (
                security_scheme,
                import_string(
                    security_scheme[X_USER_LOADER], base_module=base_module
                ),
            )
            for key, security_scheme in iteritems(security_schemes)
            if X_USER_LOADER in security_scheme
        }
