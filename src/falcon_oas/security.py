from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import iteritems

from .exceptions import SecurityError


class AccessControl(object):
    def __init__(self, security_schemes):
        self._security_schemes = security_schemes

    def handle(self, request, operation):
        if self._security_schemes and operation['security']:
            # ``requirement`` is a alternative security requirement
            # object. Only one of the security requirement objects
            # need to be satisfied to authorize a request.
            for requirement in operation['security']:
                user = self._satisfy_requirement(request, requirement)
                if user:
                    if user is not True:
                        return user
                    return
            raise SecurityError()

    def _satisfy_requirement(self, request, requirement):
        # All schemes MUST be satisfied for a request to be authorized.
        result = True
        for name, scopes in iteritems(requirement):
            user = self._satisfy_scheme(request, name, scopes)
            if not user:
                return False
            if user is not True:
                result = user
        return result

    def _satisfy_scheme(self, request, name, scopes):
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
            value = getattr(request, location).get(name)
            return satisfy(value, scopes, request)

        # Unsupported security scheme type
        return True
