# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon
import pytest
from falcon import testing

from falcon_oas.oas.exceptions import MissingRequestBody
from falcon_oas.oas.exceptions import UnmarshalError
from falcon_oas.problems import _Problem
from falcon_oas.problems import http_error_handler
from falcon_oas.problems import serialize_problem
from falcon_oas.problems import unmarshal_error_handler
from falcon_oas.problems import UnmarshalProblem


def test_problem():
    title = 'title'
    description = 'description'
    http_error = falcon.HTTPBadRequest(title=title, description=description)
    problem = _Problem(http_error)

    assert isinstance(problem, falcon.HTTPError)
    assert problem.status == falcon.HTTP_BAD_REQUEST
    assert problem.title == title
    assert problem.description == description
    assert problem.to_dict() == {
        'title': 'Bad Request',
        'status': 400,
        'detail': description,
    }


def test_problem_to_dict_without_description():
    http_error = falcon.HTTPBadRequest()
    problem = _Problem(http_error)

    assert problem.to_dict() == {'title': 'Bad Request', 'status': 400}


def test_unmarshal_problem():
    unmarshal_error = UnmarshalError(
        request_body_error=MissingRequestBody('application/json')
    )
    problem = UnmarshalProblem(unmarshal_error)

    assert problem.to_dict() == {
        'title': 'Unmarshal Error',
        'status': 400,
        'request_body': [
            {'validator': 'required', 'message': 'request body is required'}
        ],
    }


def test_serialize_problem():
    environ = testing.create_environ()
    req = falcon.Request(environ)
    resp = falcon.Response()
    problem = _Problem(falcon.HTTPBadRequest())

    serialize_problem(req, resp, problem)

    assert resp.data == b'{"title": "Bad Request", "status": 400}'
    assert resp.content_type == 'application/problem+json'
    assert resp.get_header('Vary') == 'Accept'


def test_serialize_problem_accept_json():
    environ = testing.create_environ(headers={'Accept': 'application/json'})
    req = falcon.Request(environ)
    resp = falcon.Response()
    problem = _Problem(falcon.HTTPBadRequest())

    serialize_problem(req, resp, problem)

    assert resp.content_type == 'application/json'


def test_serialize_problem_accept_html():
    environ = testing.create_environ(headers={'Accept': 'text/html'})
    req = falcon.Request(environ)
    resp = falcon.Response()
    problem = _Problem(falcon.HTTPBadRequest())

    serialize_problem(req, resp, problem)

    assert resp.content_type == 'application/json'


def test_http_error_handler():
    http_error = falcon.HTTPBadRequest()
    req = falcon.Request(testing.create_environ())
    resp = falcon.Response()
    params = {}

    with pytest.raises(_Problem):
        http_error_handler(http_error, req, resp, params)


def test_validation_error_handler():
    unmarshal_error = UnmarshalError(
        request_body_error=MissingRequestBody('application/json')
    )
    req = falcon.Request(testing.create_environ())
    resp = falcon.Response()
    params = {}

    with pytest.raises(UnmarshalProblem):
        unmarshal_error_handler(unmarshal_error, req, resp, params)
