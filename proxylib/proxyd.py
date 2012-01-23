from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer
import threading

from configuration import ConfigException

import requestreplacer
from fetcher import HLFetcher
import requestfilter
from requestfilter import RegexRequestFilter
from proxyrequesthandler import ProxyRequestHandler
from logger import FileLogger
#from win.fetchers import WindowsPlayerFetcher

import configuration
from configuration import YAMLConfigReader


class ProxyDaemonFactory:

    def _build_reqfilter(self, config):
        active = config['active']
        reqfilter = None
        if active:
            wl_file = config.get('whitelist', None)
            bl_file = config.get('blacklist', None)
            whitelist = configuration.parse_rules(wl_file)
            blacklist = configuration.parse_rules(bl_file)
            paranoid = config['paranoid']
            message = config.get('message', None)
            reqfilter = RegexRequestFilter(whitelist, blacklist, paranoid, message)
        return reqfilter

    def _build_replacer(self, config, outconfig):
        active = config['active']
        reqreplacer = None
        if active:
            reqreplacer = requestreplacer.Replacer()
            resizer_cfg = outconfig['resizer']
            rotator_cfg = outconfig['rotator']
            footer_cfg = outconfig['footer']
            cenzor_cfg = outconfig['cenzor']
            img_resizer_cfg = outconfig['imgresizer']
            if resizer_cfg['active'] or rotator_cfg['active']:
                img_handler = requestreplacer.ImageHandler()
                if resizer_cfg['active']:
                    ratio = resizer_cfg['ratio']
                    img_handler.add_resizer(ratio)
                if rotator_cfg['active']:
                    degree = rotator_cfg['degree']
                    img_handler.add_rotator(degree)
                reqreplacer.handlers.append(('image/jpeg', img_handler))
            if img_resizer_cfg['active'] or footer_cfg['active'] or cenzor_cfg['active']:
                html_handler = requestreplacer.HTMLSoupHandler()
                if img_resizer_cfg['active']:
                    ratio = img_resizer_cfg['ratio']
                    html_handler.add_img_resizer(ratio)
                if footer_cfg['active']:
                    footer_file = footer_cfg['content']
                    html_handler.add_footer()
                if cenzor_cfg['active']:
                    lista = cenzor_cfg['lista']
                    rules = configuration.parse_cenzura(lista)
                    html_handler.add_cenzor(rules)
                reqreplacer.handlers.append(('text/html(;.*)?', html_handler))
                # for handler in reqreplacer.handlers:
                #     print handler[1].ops

        return reqreplacer

    def _build_fetcher(self, config):
        voice = config['voice']
        if voice:
            fetcher = WindowsPlayerFetcher()
        else:
            fetcher = HLFetcher()
        return fetcher

    def _build_logger(self, config):
        active = config['active']
        logger = None
        if active:
            log = config['log']
            logger = FileLogger(log)
        return logger

    def create(self, config):
        reqfilter = self._build_reqfilter(config['filter'])
        replacer = self._build_replacer(config['replacer'], config)
        fetcher = self._build_fetcher(config['fetcher'])
        logger = self._build_logger(config['logger'])
        commands = ProxyCommands(reqfilter, replacer, fetcher, logger)
        general_cfg = config['general']
        host = general_cfg['host']
        port = general_cfg['port']
        addr = host, port
        proxyd = ProxyDaemon(addr, commands)
        return proxyd
    

class ProxyHTTPServer(ThreadingMixIn, HTTPServer):

    def __init__(self, addr, handler, proxy):
        HTTPServer.__init__(self, addr, handler)
        self.daemon_threads = True
        self.allow_reuse_address = True
        self.proxy = proxy


class ProxyCommands:

    def __init__(self, reqfilter=None, replacer=None, fetcher=None, logger=None):
        self.reqfilter = reqfilter
        self.replacer = replacer
        self.fetcher = fetcher
        self.logger = logger


class ProxyDaemon:

    def __init__(self, addr, commands=None):
        if commands is None:
            commands = ProxyCommands()
        self.reqfilter = commands.reqfilter
        self.replacer = commands.replacer
        self.fetcher = commands.fetcher
        self.logger = commands.logger
        self._httpserver = ProxyHTTPServer(addr, ProxyRequestHandler, self)
        self.is_serving = False

    def keep_running(self):
        return self.is_serving

    def start(self):
        self._httpserver.serve_forever()

    def stop(self):
        if self.logger is not None:
            self.logger.close()
        self._httpserver.shutdown()
        self._httpserver.socket.close()
        

def main():
    cfg_reader = YAMLConfigReader()
    config = cfg_reader.load(open('tests/data/config.yml'))
    proxy_factory = ProxyDaemonFactory()
    proxy = proxy_factory.create(config)
    proxy.start()

if __name__ == "__main__":
    main()
