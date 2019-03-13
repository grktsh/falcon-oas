"""Define OpenAPI Specification Extensions for falcon-oas."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#: ``x-falcon-oas-implementor`` associates Path Item Object and
#: Security Scheme Object to implementations respectively.
#:
#: Path Item Object can be associated to Falcon resource class:
#:
#: .. code:: yaml
#:
#:     /v1/pets:
#:       x-falcon-oas-implementor: api.v1.pets.Collection
#:       get:
#:         responses:
#:           '200':
#:             description: Return a pet list
#:             content:
#:               application/json:
#:                 schema:
#:                   $ref: '#/components/schemas/PetList'
#:
#: :func:`~.routing.generate_routes` yields tuples of the uri template
#: and the Falcon resource class.  Using
#: :func:`~.routing.generate_routes`, :class:`~.OAS`
#: calls ``falcon.API.add__route`` with ``/v1/pets`` and an instance of
#: ``api.v1.pets.Collection`` automatically in this case.
#:
#: Security Scheme Object can be associated to access control
#: callable:
#:
#: .. code:: yaml
#:
#:     x-falcon-oas-implementor: auth.session_cookie_loader
#:     type: apiKey
#:     name: session
#:     in: cookie
#:
#: When Operation Object defines Security Requirement Object directly
#: or indirectly from top-level ``security``,
#: :class:`~.middlewares.security.SecurityMiddleware` calls
#: the access control callable with the value of ``session`` cookie,
#: the scopes of Security Requirement Object and an instance of
#: :class:`~.oas.Request`.
#:
#: The access control callable should return:
#:
#: ``True``
#:     Allow the access.
#:
#: Truthy value other than ``True`` as authenticated user
#:     Allow the access.  The return value is stored in
#:     ``req.context['oas.user']``.
#:
#: Falsy value
#:     Deny the access.  403 Forbidden is raised.
FALCON_OAS_IMPLEMENTOR = 'x-falcon-oas-implementor'
