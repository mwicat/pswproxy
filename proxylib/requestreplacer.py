import re
import Image
import image_util
from common import ProxyResponse
from StringIO import StringIO
from BeautifulSoup import BeautifulSoup, Tag, NavigableString


class ContentHandler:

    def handle(self, response):
        pass

class ImageHandler(ContentHandler):

    MIME_FORMATS = {'image/jpeg': 'jpeg',
                    'image/gif': 'gif',
                    'image/bmp': 'bmp',
                    'image/png': 'png'}

    def __init__(self, ops=[]):
        self.ops = ops

    def add_resizer(self, ratio):
        resizer = lambda im: image_util.resize(im, ratio)
        self.ops.append(resizer)

    def add_rotator(self, degree):
        rotator = lambda im: im.rotate(degree)
        self.ops.append(rotator)

    def get_image(self, response):
        data = response.read()
        strio = StringIO(data)
        im = Image.open(strio)
        return im

    def handle(self, response):
        im = self.get_image(response)
        im = self.process_image(im)
        format = self.MIME_FORMATS[response.get_ctype()]
        mode = 'RGB'
        tn_data = im.tostring(format, mode)
        response.setheader('Content-Length', str(len(tn_data)))
        response.setbody(StringIO(tn_data))
        return response

    def process_image(self, im):
        for op in self.ops:
            im = op(im)
        return im


class HTMLHandler(ContentHandler):

    pass

class HTMLSoupHandler():

    def __init__(self, ops=[]):
        self.ops = ops

    def add_footer(self):
        def footer_op(soup):
            head_el = soup.find("head")
            body_el = soup.find("body")
            footer_attachable = not (head_el is None or body_el is None)

            if footer_attachable:
                footer_wrap_el = Tag(soup, "div")
                footer_wrap_el['style'] = "position: fixed; width: 100%; height: auto; z-index: 10000; bottom: 0pt; display: block;"
                footer_el = Tag(soup, "div")
                footer_el['style'] = "background-color: rgb(15, 25, 35); color: white; height: auto"
                footer_text = NavigableString(open("footer.html").read())
                footer_el.append(footer_text)
                footer_wrap_el.append(footer_el)
                body_el.append(footer_wrap_el)
        self.ops.append(footer_op)

    def add_img_resizer(self, ratio):
        def resize_op(soup):
            imgs = soup.findAll('img')
            for img in imgs:
                if img.has_key('width') and img.has_key('height'):
                    w = int(img['width'].rstrip('px'))
                    h = int(img['height'].rstrip('px'))
                    w = int(round(ratio * w))
                    h = int(round(ratio * h))
                    img['width'] = w
                    img['height'] = h
        self.ops.append(resize_op)

    def handle(self, response):
        data = response.read()
        soup_tree = BeautifulSoup(data)
        for op in self.ops:
            op(soup_tree)
        data = soup_tree.prettify()
        response.setheader('Content-Length', str(len(data)))
        response.setbody(StringIO(data))
        return response

class ExeHandler(ContentHandler):

    pass

class Replacer:

    default_handlers = [
        ('image/(png|gif|jpeg)', ImageHandler()),
        ('text/html|application/xhtml\+xml', HTMLSoupHandler()),
        ('binary/executable', ExeHandler()),
        ]

    def __init__(self, handlers=None):
        if handlers is not None:
            self.handlers = handlers
        else:
            self.handlers = Replacer.default_handlers

    def replace(self, response):
        ctype = response.get_ctype()
        if ctype is not None:
            for ct, handler in self.handlers:
                ct = '^' + ct + '$'
                if re.search(ct, ctype):
                    response = handler.handle(response)
        return response
