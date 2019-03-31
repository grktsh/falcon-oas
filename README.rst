falcon-oas
==========

.. image:: https://img.shields.io/pypi/v/falcon-oas.svg
   :alt: PyPI
   :target: https://pypi.org/project/falcon-oas

.. image:: https://img.shields.io/travis/grktsh/falcon-oas/master.svg
   :alt: Travis
   :target: https://travis-ci.org/grktsh/falcon-oas

.. image:: https://img.shields.io/codecov/c/github/grktsh/falcon-oas/master.svg
   :alt: Codecov
   :target: https://codecov.io/gh/grktsh/falcon-oas

Prerequisites
-------------

- Validated OpenAPI 3 document

  - falcon-oas does not validate OpenAPI 3 document itself at runtime.  It should be validated in advance.

Features
--------

- Request validation and unmarshaling
- Access control
- Association of Path Item Objects and resource classes in Falcon

Example
-------

.. code:: python

    class PetItem:
        def on_get(self, req, resp, pet_id):
            pet = get_pet_by_id(pet_id)
            resp.media = pet.to_dict()

        def on_delete(self, req, resp, pet_id):
            pet = delete_pet_by_id(pet_id)
            resp.status = falcon.HTTP_NO_CONTENT


    with open('/path/to/openapi.json') as f:
        spec_dict = json.load(f)
    api = falcon_oas.OAS(spec_dict).create_api()

Here is the part of its OpenAPI 3 document in YAML:

.. code:: yaml

    paths:
      /api/v1/pets/{pet_id}:
        x-falcon-oas-implementation: path.to.PetItem
        get:
          responses:
            '200':
              description: A pet.
        delete:
          responses:
            '204':
              description: Successful deletion.
          security:
          - api_key: []
        parameters:
        - name: pet_id
          in: path
          required: true
          schema:
            type: integer
    components:
      securitySchemes:
        api_key:
          x-falcon-oas-implementation: path.to.api_key_validator
          type: apiKey
          name: X-API-Key
          in: header

``pet_id`` path parameter is unmarshaled to ``int`` without `Field Converters <https://falcon.readthedocs.io/en/stable/api/routing.html#field-converters>`_ since it is defined as ``integer`` type.

``DELETE /api/v1/pets/{pet_id}`` requests are protected by the ``api_key`` security scheme. The corresponding responder is processed only if it grants the request. Otherwise, 403 Forbidden error occurs automatically.

``x-falcon-oas-implementation`` associates Path Item Object and the REST resource class in Falcon so that falcon-oas automatically calls ``falcon.API.add_route`` with its path and the resource instance.

Also ``x-falcon-oas-implementation`` associates Security Scheme Object and the access control function so that falcon-oas automatically handles Security Requirement Object in each request. See ``falcon_oas.extensions`` for details.

``req.context['oas']``
----------------------

``req.context['oas'].user``
    Authorized user.

``req.context['oas'].parameters``
    Unmarshaled request parameters in dict.

``req.context['oas'].request_body``
    Unmarshaled request body.

Problems
--------

Media Type: ``application/problem+json`` only

Unmarshal Error
~~~~~~~~~~~~~~~

HTTP status code: 400

- ``"type"``: ``"https://pypi.org/project/falcon-oas/0.3.0/#unmarshal-error"``
- ``"title"``: ``"Unmarshal Error"``
- ``"status"``: ``400``
- ``"parameters"``: (optional) The array of parameter error objects
- ``"request_body"``: (optional) The array of request body error objects

The parameter error object and the request body error object have the following members from ``jsonschema.ValidationError``:

- ``"path"``: The path to the offending element within the instance
- ``"validator"``: The name of the failed validator
- ``"message"``: A human readable message explaining the error

Example:

.. code:: json

    {
      "type": "https://pypi.org/project/falcon-oas/0.3.0/#unmarshal-error",
      "title": "Unmarshal Error",
      "status": 400,
      "parameters": [
        {
          "path": ["path", "pet_id"],
          "validator": "type",
          "message": "'me' is not of type 'integer'"
        }
      ],
      "request_body": [
        {
          "path": ["name"],
          "validator": "type",
          "message": "42 is not of type 'string'"
        }
      ]
    }
