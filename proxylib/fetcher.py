# -*- coding: iso-8859-2 -*-
import httplib
from common import ProxyResponse
import urlparse

import sys

class HLFetcher:

    TIMEOUT = 4

    def fetch(self, host, path, body, hdrs):
        urlpr = urlparse.urlparse(path)
        u = ('', '') + urlpr[2:]
        path = urlparse.urlunparse(u)
        method = "POST" if body is not None else "GET"
        conn = httplib.HTTPConnection(host, timeout=self.TIMEOUT)
        conn.request(method, path, body, hdrs)
        response = conn.getresponse()
        print 'response', response
        return ProxyResponse(response)


class PlayerFetcher(HLFetcher):

    def fetch(self, host, path, body, hdrs):
        if body is not None and 'content-type' in hdrs and hdrs['content-type'].startswith('application/x-www-form-urlencoded'):
            data = body.getvalue()
            form = urlparse.parse_qs(data)
            self.play(path, form)
        return HLFetcher.fetch(self, host, path, body, hdrs)
