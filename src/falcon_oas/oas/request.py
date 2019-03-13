from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import abc

import six

from ..utils import cached_property

if six.PY2:  # pragma: no cover
    abstractproperty = abc.abstractproperty
else:  # pragma: no cover

    def abstractproperty(f):
        return property(abc.abstractmethod(f))


@six.add_metaclass(abc.ABCMeta)
class Request(object):
    @abstractproperty
    def uri_template(self):
        """Return the key of Path Item Object with the base path."""

    @abstractproperty
    def method(self):
        """Return the HTTP method of Operation Object."""

    @cached_property
    @abc.abstractmethod
    def parameters(self):
        """Return the dict of request parameters.

        Example:

        .. code:: python

            {
                'query': {'page': '1'},
                'header': {'X-API-Key': 'secret'},
                'path': {'id': '42'},
                'cookie': {'session': 'secret'},
            }
        """

    @abstractproperty
    def media_type(self):
        """Return the media type of the request without parameter."""

    @abc.abstractmethod
    def get_media(self):
        """Return deserialized request body."""
