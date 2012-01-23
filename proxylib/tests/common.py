import mox
import sys
from socket import socket
sys.path.append('../..')
from proxylib.common import ProxyResponse
from StringIO import StringIO

class ResponseBuffer(StringIO):

    def close(self):
        self.text = self.getvalue()
        StringIO.close(self)
    

def create_response_mock():
    resp_mock = mox.MockObject(ProxyResponse)
    attrs = 'msg', 'version', 'status', 'reason'
    for attr in attrs:
        setattr(resp_mock, attr, None)
    return resp_mock

def create_request_mock():
    resp_mock = mox.MockObject(socket)
    return resp_mock
