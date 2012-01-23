import threading

import proxylib.configuration as config
import proxylib.proxyd as proxyd


class ProxyWorker(threading.Thread):

    def __init__(self, proxy):
        threading.Thread.__init__(self)
        self.proxy = proxy

    def run(self):
        self.proxy.start()

class Controller:

    PROXY_FACTORY = proxyd.ProxyDaemonFactory()

    def __init__(self, cfg_fname):
        self.proxy = None
        self.cfg_fname = cfg_fname
        self.cfg_reader = config.YAMLConfigReader()

    def _reload_config(self):
        self.cfg_file = open(self.cfg_fname)
        self.cfg = self.cfg_reader.load(self.cfg_file)

    def get_running(self):
        return self.proxy is not None

    def start(self):
        self._reload_config()
        if self.proxy is None:
            self.proxy = Controller.PROXY_FACTORY.create(self.cfg)
            proxyworker = ProxyWorker(self.proxy)
            proxyworker.start()

    def stop(self):
        if self.proxy is not None:
            self.proxy.stop()
            self.proxy = None

    def restart(self):
        self.stop()
        self.start()
