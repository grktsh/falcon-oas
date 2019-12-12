from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict

import falcon


UNMARSHAL_PROBLEM_VERSION = '0.3.0'
UNMARSHAL_PROBLEM_TYPE_URI = (
    'https://pypi.org/project/falcon-oas/'
    + UNMARSHAL_PROBLEM_VERSION
    + '/#unmarshal-error'
)


class Problem(falcon.HTTPError):
    def __init__(
        self,
        status,
        title=None,
        description=None,
        headers=None,
        code=None,
        type_uri=None,
        additional_members=None,
    ):
        if title == status:
            title = status[4:]

        super(Problem, self).__init__(
            status,
            title=title,
            description=description,
            headers=headers,
            code=code,
        )
        self.type_uri = type_uri
        self.additional_members = additional_members

    @classmethod
    def from_http_error(cls, error):
        return cls(
            error.status,
            title=error.title,
            description=error.description,
            headers=error.headers,
            code=error.code,
        )

    def to_dict(self, obj_type=dict):
        obj = obj_type()
        if self.type_uri is not None:
            obj['type'] = self.type_uri
        obj['title'] = self.title
        obj['status'] = int(self.status[:3])
        if self.description is not None:
            obj['detail'] = self.description
        if self.additional_members is not None:
            obj.update(obj_type(self.additional_members))
        return obj


def serialize_problem(req, resp, problem):
    """Serialize the given instance of Problem."""
    preferred = req.client_prefers(
        ('application/json', 'application/problem+json')
    )
    if preferred is None:
        preferred = 'application/json'

    resp.data = problem.to_json().encode('utf-8')
    resp.content_type = preferred
    resp.append_header('Vary', 'Accept')


def http_error_handler(error, req, resp, params):
    raise Problem.from_http_error(error)


def undocumented_media_type_handler(error, req, resp, params):
    raise Problem.from_http_error(falcon.HTTPBadRequest())


def security_error_handler(error, req, resp, params):
    raise Problem.from_http_error(falcon.HTTPForbidden())


def unmarshal_error_handler(error, req, resp, params):
    raise Problem(
        falcon.HTTP_BAD_REQUEST,
        title='Unmarshal Error',
        type_uri=UNMARSHAL_PROBLEM_TYPE_URI,
        additional_members=error.to_dict(obj_type=OrderedDict),
    )
