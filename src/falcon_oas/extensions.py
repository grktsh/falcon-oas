"""Define OpenAPI Specification Extensions for falcon-oas."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

#: ``x-falcon-oas-implementation`` associates Path Item Object and
#: Security Scheme Object to implementations respectively.
#:
#: Path Item Object can be associated to Falcon resource class:
#:
#: .. code:: yaml
#:
#:     /v1/pets:
#:       x-falcon-oas-implementation: api.v1.pets.Collection
#:       get:
#:         responses:
#:           '200':
#:             description: Return a pet list
#:             content:
#:               application/json:
#:                 schema:
#:                   $ref: '#/components/schemas/PetList'
#:
#: falcon-oas calls ``falcon.API.add_route`` with ``/v1/pets`` and an
#: instance of``api.v1.pets.Collection`` automatically in this case.
#:
#: Security Scheme Object can be associated to access control
#: function:
#:
#: .. code:: yaml
#:
#:     x-falcon-oas-implementation: auth.session_cookie_loader
#:     type: apiKey
#:     name: session
#:     in: cookie
#:
#: When Operation Object defines Security Requirement Object directly
#: or indirectly from top-level ``security``, falcon-oas calls
#: the access control function with the value of ``session`` cookie,
#: the scopes of Security Requirement Object and an instance of
#: :class:`oas.Request` in this case.
#:
#: The access control function should return:
#:
#: ``True``
#:     Allow the access.
#:
#: Truthy value other than ``True`` as authenticated user
#:     Allow the access. The return value is stored as
#:     ``req.context['oas'].user``.
#:
#: Falsy value
#:     Deny the access. 403 Forbidden error occurs.
IMPLEMENTATION = 'x-falcon-oas-implementation'
