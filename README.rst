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

Problems
--------

Media Type: ``application/problem+json`` only

Unmarshal Problem
~~~~~~~~~~~~~~~~~

HTTP status code: 400

- ``"type"``: ``"https://pypi.org/project/falcon-oas/0.3.0/#unmarshal-problem"``
- ``"title"``: ``"Unmarshal Error"``
- ``"status"``: ``400``
- ``"request_body"``: (optional) The array of request body error objects
- ``"parameters"``: (optional) The object with key of ``"query"``, ``"header"``, ``"path"`` or ``"cookie"``, whose value is the array of parameter error objects

The request body error object has the following members from ``jsonschema.exceptions.ValidationError``:

- ``"path"``: The path to the offending element within the instance
- ``"validator"``: The name of the failed validator
- ``"message"``: A human readable message explaining the error

The parameter error object also has the member ``"name"``:

- ``"name"``: The name of the parameter

Example:

.. code:: json

    {
      "type": "https://pypi.org/project/falcon-oas/0.3.0/#unmarshal-problem",
      "title": "Unmarshal Error",
      "status": 400,
      "request_body": [
        {
          "path": ["name"],
          "validator": "type",
          "message": "42 is not of type 'string'"
        }
      ],
      "parameters": {
        "path": [
          {
            "name": "pet_id",
            "path": [],
            "validator": "type",
            "message": "'me' is not of type 'integer'"
          }
        ]
      }
    }
