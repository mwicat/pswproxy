# -*- coding: iso-8859-2 -*-
from proxylib.fetcher import PlayerFetcher
import urlparse
import pyivona.winutil

class WindowsPlayerFetcher(PlayerFetcher):

    IVONA = pyivona.winutil.IvonaPlayer()

    TEXT = u"Na stronie %s Użytkownik wypełnił następujące pola:"

    def play(self, url, form):
        host = urlparse.urlparse(url).hostname
        field_msgs = [WindowsPlayerFetcher.TEXT % host]
        for field, value in form.items():
            t = '%s to %s' % (field, value[0])
            field_msgs.append(t)
        ivotext = ' '.join(field_msgs)
        self.IVONA.say(ivotext)


def testWinPlayer():
    player_fetcher = WindowsPlayerFetcher()
    form = {'login': 'marek', 'password': 'marek'}
    player_fetcher.play(form)
    import time
    time.sleep(5)

if __name__ == "__main__":
    testWinPlayer()
