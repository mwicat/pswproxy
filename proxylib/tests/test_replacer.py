import unittest
import mox
import Image
from StringIO import StringIO
from mimetools import Message
from common import create_response_mock

import sys
sys.path.append('../..')
from proxylib.common import ProxyResponse
from proxylib.replacer import Replacer, HTMLHandler, ImageHandler

class ReplacerTestCase(unittest.TestCase):

    def testHandlerAvail(self):
        resp_mock = create_response_mock()
        resp_mock.getheader("Content-Type").AndReturn("application/xhtml+xml")
        mox.Replay(resp_mock)

        handler_mock = mox.MockObject(HTMLHandler)
        handler_mock.handle(resp_mock).AndReturn(resp_mock)
        mox.Replay(handler_mock)

        replacer = Replacer([('text/html|application/xhtml\+xml', handler_mock)])
        replacer.replace(resp_mock)
        mox.Verify(resp_mock)
        mox.Verify(handler_mock)

    def testHandlerNotAvail(self):
        resp_mock = create_response_mock()
        resp_mock.getheader("Content-Type").AndReturn("text/html")
        mox.Replay(resp_mock)

        replacer = Replacer([])
        resp = replacer.replace(resp_mock)
        mox.Verify(resp_mock)
        assert resp == resp_mock


class ImageHandlerTestCase(unittest.TestCase):

    def setUp(self):
        imgfile = open('data/image_resp_body.jpg', 'rb')
        self.img_data = imgfile.read()
        self.img = Image.open(StringIO(self.img_data))

    def _img_cmp_size(self, im, im2, ratio):
        w, h = im.size
        w2, h2 = im2.size
        expw = w * ratio
        exph = h * ratio
        delta = 1e-5
        return abs(expw - w2) < delta and abs(exph - h2) < delta

    def testResize(self):
        ratio = 0.5
        resp_mock = create_response_mock()
        resp_mock.getheader("Content-Type").AndReturn("image/jpeg")
        resp_mock.read().AndReturn(self.img_data)

        cmp_len = lambda new_data: len(new_data) < len(self.img_data)
        resp_mock.setheader('Content-Length', mox.Func(cmp_len))

        cmp_size = lambda im: self._img_cmp_size(self.img, Image.open(im), ratio)
        resp_mock.setbody(mox.Func(cmp_size))

        mox.Replay(resp_mock)

        img_handler = ImageHandler()
        img_handler.add_resizer(ratio)
        replacer = Replacer([('image/jpeg', img_handler)])
        resp = replacer.replace(resp_mock)
        mox.Verify(resp_mock)

class HTMLHandlerTestCase(unittest.TestCase):

    pass
    

if __name__ == "__main__":
    unittest.main()
