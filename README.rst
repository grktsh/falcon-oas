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

  - OpenAPI 3 document should be validated in advance just like the source code is tested in advance.

Features
--------

- Request validation and unmarshaling
- Access control
- Association of Path Item Objects and resource classes in Falcon

Example
-------

If there is the following Falcon API implementation:

.. code:: python

    class PetItem:
        def on_get(self, req, resp, pet_id):
            pet = get_pet_by_id(pet_id)
            resp.media = pet.to_dict()

        def on_delete(self, req, resp, pet_id):
            if not is_valid_api_key(req.get_header('X-API-Key')):
                raise falcon.HTTPForbidden()

            delete_pet_by_id(pet_id)
            resp.status = falcon.HTTP_NO_CONTENT


    api = falcon.API()
    api.add_route('/api/v1/pets/{pet_id:int}', PetItem())

Here is the falcon-oas implementation:

.. code:: python

    class PetItem:
        def on_get(self, req, resp, pet_id):
            pet = get_pet_by_id(pet_id)
            resp.media = pet.to_dict()

        def on_delete(self, req, resp, pet_id):
            pet = delete_pet_by_id(int(pet_id))
            resp.status = falcon.HTTP_NO_CONTENT


    with open('/path/to/openapi.json') as f:
        spec_dict = json.load(f)
    api = falcon_oas.OAS(spec_dict).create_api()

and the part of its OpenAPI 3 document:

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

``x-falcon-oas-implementation`` associates Path Item Object and the REST resource class in Falcon so that falcon-oas automatically calls ``falcon.API.add_route`` with its path and the resource instance.

Also ``x-falcon-oas-implementation`` associates Security Scheme Object and the access control function so that falcon-oas automatically handles Security Requirement Object in each request. See ``falcon_oas.extensions`` for details.

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
