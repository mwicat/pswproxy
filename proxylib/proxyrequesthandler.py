from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO

def try_replace(replacer, response):
    try:
        response = replacer.replace(response)
    except Exception:
        pass
    return response


class ProxyRequestHandler(BaseHTTPRequestHandler):

    def do_request(self, body=None):
        host = self.headers.getheader('Host')
        url = self.path
        
        self.headers['Accept-Encoding'] = ''
        hdrs = dict(self.headers)

        proxy = self.server.proxy
        fetcher = proxy.fetcher
        replacer = proxy.replacer
        logger = proxy.logger
        filter = proxy.reqfilter

        if filter is not None:
            passed = filter.check(url)
        else:
            passed = True

        if logger is not None:
            logger.log(self.client_address, url, passed)

        if passed:
            if fetcher is not None:
                response = fetcher.fetch(host, self.path, body, hdrs)
                if replacer is not None:
                    response = try_replace(replacer, response)
                self._handle_response(response)
            else:
                self.send_error(403, u"Pobieranie zasobow nieczynne!")
        else:
            if filter.message is not None:
                message = open(filter.message).read()
                self._handle_deny(message)
            else:
                self.send_error(403, u'Access denied by The Bastard Operator From Hell')

    def do_GET(self):
        self.do_request()
    
    def do_POST(self):
        clen = int(self.headers['Content-Length'])
        data = self.rfile.read(clen)
        body = StringIO(data)
        self.do_request(body)

    def _handle_deny(self, message):
        #self.send_error(403, "Brak dostepu!")
        self.send_response(403)
        self.end_headers()
        self.wfile.write(message)


    def _handle_response(self, response):
        self.send_response(response.status, response.reason)
        headers = response.headers
        self.wfile.write(str(response.headers))
        self.end_headers()
        body = response.read()
        self.wfile.write(body)
