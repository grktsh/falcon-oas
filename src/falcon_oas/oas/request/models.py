from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six

if six.PY2:  # pragma: no cover
    abstractproperty = abc.abstractproperty
else:  # pragma: no cover

    def abstractproperty(f):
        return property(abc.abstractmethod(f))


@six.add_metaclass(abc.ABCMeta)
class RequestParameters(object):
    @abstractproperty
    def path(self):
        """Return the path parameters."""

    @abstractproperty
    def query(self):
        """Return the query parameters."""

    @abstractproperty
    def header(self):
        """Return the header parameters."""

    @abstractproperty
    def cookie(self):
        """Return the header parameters."""


@six.add_metaclass(abc.ABCMeta)
class RequestBody(object):
    @abstractproperty
    def content_length(self):
        """Return the content length."""

    @abstractproperty
    def media_type(self):
        """Return the media type of the request without parameter."""

    @abstractproperty
    def media(self):
        """Return deserialized request body."""


@six.add_metaclass(abc.ABCMeta)
class Request(RequestParameters, RequestBody):
    @abstractproperty
    def uri_template(self):
        """Return the key of Path Item Object with the base path."""

    @abstractproperty
    def method(self):
        """Return the HTTP method of Operation Object."""

    @abstractproperty
    def context(self):
        """Return the request context."""
