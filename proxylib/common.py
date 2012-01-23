from mimetools import Message
from StringIO import StringIO

class ProxyResponse:

    def __init__(self, httpresponse=None):
        if httpresponse is not None:
            self.headers = httpresponse.msg
            self.version = httpresponse.version
            self.status = httpresponse.status
            self.reason = httpresponse.reason
            self._body_buf = httpresponse

    def get_ctype(self):
        try:
            ctype = self.getheader('Content-Type')
        except KeyError:
            ctype = None
        return ctype

    def getheader(self, name):
        return self.headers[name]

    def setheader(self, name, value):
        self.headers[name] = value

    def setheaders(self, headers):
        if isinstance(headers, basestring):
            strio = StringIO(headers)
            self.headers = Message(strio)
        else:
            self.headers = headers

    def read(self, amt=None):
        if amt is None:
            data = self._body_buf.read()
        else:
            data = self._body_buf.read(amt)
        return data

    def setbody(self, body_buf):
        self._body_buf = body_buf
