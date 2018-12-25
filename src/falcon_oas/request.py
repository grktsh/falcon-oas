from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import falcon


class Request(falcon.Request):
    @property
    def host_url(self):
        return self.scheme + '://' + self.netloc

    @property
    def oas_query(self):
        return self.context['oas.parameters']['query']

    @property
    def oas_header(self):
        return self.context['oas.parameters']['header']

    @property
    def oas_cookie(self):
        return self.context['oas.parameters']['cookie']

    @property
    def oas_media(self):
        return self.context['oas.request_body']

    @property
    def oas_user(self):
        return self.context['oas.user']
