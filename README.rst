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
