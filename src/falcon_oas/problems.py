from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon


class _Problem(falcon.HTTPError):
    """Represents predefined problem type of RFC 7807."""

    has_representation = True

    def __init__(self, http_error):
        super(_Problem, self).__init__(
            http_error.status,
            title=http_error.title,
            description=http_error.description,
        )

    def to_dict(self, obj_type=dict):
        obj = obj_type()
        obj['title'] = self.status[4:]
        obj['status'] = int(self.status[:3])
        if self.description is not None:
            obj['detail'] = self.description
        return obj


class UnmarshalProblem(falcon.HTTPError):

    has_representation = True

    def __init__(self, unmarshal_error):
        super(UnmarshalProblem, self).__init__(
            falcon.HTTP_BAD_REQUEST, title='Unmarshal Error'
        )
        self.unmarshal_error = unmarshal_error

    def to_dict(self, obj_type=dict):
        obj = obj_type()
        obj['title'] = self.title
        obj['status'] = int(self.status[:3])
        obj.update(self.unmarshal_error.to_dict(obj_type=obj_type))
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


def http_error_handler(http_error, req, resp, params):
    raise _Problem(http_error)


def unmarshal_error_handler(unmarshal_error, req, resp, params):
    raise UnmarshalProblem(unmarshal_error)
