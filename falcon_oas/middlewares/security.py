from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
from six import iteritems

from ..extensions import X_USER_LOADER
from ..utils import import_string


class SecurityMiddleware(object):
    def __init__(self, spec, security_schemes):
        self.spec = spec
        self.security_schemes = security_schemes

    def process_resource(self, req, resp, resource, params):
        operation = self.spec.get_operation(
            req.uri_template, req.method.lower()
        )
        if operation is None:
            # Undocumented request
            return

        if operation['security']:
            if not any(
                self._satisfy_requirement(req, requirement)
                for requirement in operation['security']
            ):
                # TODO: distinguish unauthorized error from forbidden error
                raise falcon.HTTPForbidden()

    def _satisfy_requirement(self, req, requirement):
        return all(
            self._satisfy_scheme(req, key, scopes)
            for key, scopes in iteritems(requirement)
        )

    def _satisfy_scheme(self, req, key, scopes):
        security_scheme, user_loader = self.security_schemes[key]
        if security_scheme['type'] == 'apiKey':
            location = security_scheme['in']
            name = security_scheme['name']
            try:
                value = _get_api_key(req, location, name)
            except (KeyError, falcon.HTTPMissingHeader):
                return False
            user = user_loader(value)
            if user and user is not True:
                req.context['oas.user'] = user
            return user
        # Unsupported yet
        return True


def _get_api_key(req, location, name):
    if location == 'cookie':
        return req.cookies[name]
    if location == 'header':
        return req.get_header(name, required=True)
    if location == 'query':
        return req.params[name]
    # NOTREACHED
    return  # pragma: no cover


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
