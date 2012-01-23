import unittest
import mox
import Image
from StringIO import StringIO
from mimetools import Message
from common import create_response_mock, create_request_mock

import sys
sys.path.append('../..')

from proxylib import requestreplacer
from proxylib.requestreplacer import Replacer
from proxylib.common import ProxyResponse
from proxylib.proxyd import ProxyDaemon, ProxyCommands, ProxyDaemonFactory
from proxylib.proxyrequesthandler import ProxyRequestHandler
from proxylib import requestfilter
from proxylib.requestfilter import RegexRequestFilter
from proxylib.logger import RequestLogger
from proxylib.config import YAMLConfigReader

from common import ResponseBuffer

class RequestHandlerTestCase(unittest.TestCase):

    def setUp(self):
        self.request_mock = create_request_mock()
        self.client_response = ResponseBuffer()
        self.request_path = '/'
        self.host = 'www.google.pl'
        self.url = 'http://' + self.host + self.request_path

        self.client_request = StringIO('GET %s HTTP/1.0\r\nHost: %s\r\n\r\n' % (self.request_path, self.host))
        self.request_mock.makefile(mox.IgnoreArg(), mox.IgnoreArg()).AndReturn(self.client_request)
        self.request_mock.makefile(mox.IgnoreArg(), mox.IgnoreArg()).AndReturn(self.client_response)
        mox.Replay(self.request_mock) 
       
        self.addr = 'www.google.pl', 80
        self.client_addr = 'localhost', 34000
        self.proxy_addr = 'localhost', 3128
        self.server = ProxyDaemon(self.proxy_addr)

    def testRequestImage(self):
        img_handler = requestreplacer.ImageHandler()
        img_handler.add_resizer(0.5)
        replacer = Replacer([('image/jpeg', img_handler)])
        reqfilter = mox.MockAnything()
        logger = mox.MockAnything()

        response = ProxyResponse()
        response.setheaders('Content-Type: image/jpeg\r\n')
        response.version = 'HTTP/1.0'
        response.status = 200
        response.reason = ''
        response.setbody(open('data/image_resp_body.jpg', 'rb'))

        class Fetcher:
            def fetch(self, host, path, body, headers): return response
        fetcher = Fetcher()

        self.server.reqfilter = reqfilter
        self.server.replacer = replacer
        self.server.fetcher = fetcher
        self.server.logger = logger
        # commands = ProxyCommands(reqfilter, replacer, fetcher, logger)
        req_handler = ProxyRequestHandler(self.request_mock, self.client_addr, self.server)
        mox.Verify(self.request_mock)

    def testLogging(self):
        logger = mox.MockObject(RequestLogger)
        logger.log(self.url, True)
        mox.Replay(logger)

        response = ProxyResponse()
        response.setheaders('Content-Type: image/jpeg\r\n')
        response.version = 'HTTP/1.0'
        response.status = 200
        response.reason = ''
        response.setbody(open('data/image_resp_body.jpg', 'rb'))

        class Fetcher:
            def fetch(self, host, path, body, headers): return response
        fetcher = Fetcher()

        self.server.logger = logger
        self.server.fetcher = fetcher
        req_handler = ProxyRequestHandler(self.request_mock, self.client_addr, self.server)
        mox.Verify(self.request_mock)
        mox.Verify(logger)
        
    def testFiltering(self):
        reqfilter = RegexRequestFilter(whitelist=[self.url])
        self.server.reqfilter = reqfilter
        req_handler = ProxyRequestHandler(self.request_mock, self.client_addr, self.server)


class ProxyFactoryTestCase(unittest.TestCase):

    def testPopulateConfig(self):
        cfg_reader = YAMLConfigReader()
        config = cfg_reader.load(open('data/config.yml'))
        proxy_factory = ProxyDaemonFactory()
        proxy = proxy_factory.create(config)


if __name__ == "__main__":
    unittest.main()
