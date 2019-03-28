from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

import falcon
from six import iteritems

from .. import extensions
from ..oas.exceptions import SecurityError
from ..oas.security import AccessControl
from ..utils import import_string

logger = logging.getLogger(__name__)


class SecurityMiddleware(object):
    def __init__(self, security_schemes):
        self._access_control = AccessControl(security_schemes)

    def process_resource(self, req, resp, resource, params):
        oas = req.context['oas']
        if not oas:
            return

        try:
            oas.user = self._access_control.handle(
                oas.request, oas.operation
            )
        except SecurityError:
            logger.warning(
                'No security requirement was satisfied: %r',
                oas.operation['security'],
            )
            # TODO: distinguish unauthorized error from forbidden error
            raise falcon.HTTPForbidden()


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
