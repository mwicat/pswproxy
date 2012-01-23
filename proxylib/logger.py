# -*- coding: iso-8859-2 -*-

import datetime

class RequestLogger:

    def __init__(self):
        pass

    def log(self, request, passed):
        pass

class FileLogger(RequestLogger):

    def __init__(self, log):
        self.logfile = open(log, 'a')

    def log(self, src_ip, url, passed):
        msg_fmt = u'[%s] żądanie od %s do: %s -- %s\n'
        tm = datetime.datetime.now()
        passinfo = 'przepuszczono' if passed else 'zablokowano'
        line = msg_fmt % (tm, src_ip, url, passinfo)
        self.logfile.write(line.encode('cp1250'))

    def close(self):
        self.logfile.close()
