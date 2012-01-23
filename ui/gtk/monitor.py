#!/usr/bin/env python
# -*- coding: iso-8859-2 -*-

import gtk
gtk.gdk.threads_init()
from ui.control import Controller

import os
    
class StatusIcc:

    def activate( self, widget, data=None):
        pass

    def popup(self, button, widget, time, data=None):
        self.menu.show_all()
        self.menu.popup(None, None, None, 3, time)

    def __init__(self, app):
        self.app = app
        self.staticon = gtk.StatusIcon()
        self.staticon.connect("activate", self.restart_proxy)
        self.staticon.connect("popup_menu", self.popup)
        self.staticon.set_visible(True)
        self._build_menu()
        self.start_proxy(self)
        gtk.main()

    def start_proxy(self, widget=None):
        self.set_started()
        self.app.ctrl.start()

    def stop_proxy(self, widget=None):
        self.set_stopped()
        self.app.ctrl.stop()

    def restart_proxy(self, widget=None):
        self.set_stopped()
        self.staticon.set_blinking(True)
        self.app.ctrl.restart()
        self.set_started()
        self.staticon.set_blinking(False)

    def set_stopped(self):
        self.staticon.set_tooltip(u'PSWProxy disabled')
        self.staticon.set_from_file("proxy_down.png")

    def set_started(self):
        self.staticon.set_tooltip(u'PSWProxy enabled')
        self.staticon.set_from_file("proxy_up.png")
        
    def _build_menu(self):
        self.menu = gtk.Menu()
        menuItem = gtk.ImageMenuItem(gtk.STOCK_CONNECT)
        menuItem.child.set_text(u'Enable')
        menuItem.connect('activate', self.start_proxy)
        self.menu.append(menuItem)

        menuItem = gtk.ImageMenuItem(gtk.STOCK_STOP)
        menuItem.child.set_text(u'Disable')
        menuItem.connect('activate', self.stop_proxy)
        self.menu.append(menuItem)

        menuItem = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
        menuItem.child.set_text(u'Restart')
        menuItem.connect('activate', self.restart_proxy)
        self.menu.append(menuItem)

        menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        menuItem.child.set_text(u'Quit')
        menuItem.connect('activate', self.quit)
        self.menu.append(menuItem)

    def quit(self, widget):
        self.stop_proxy(widget)
        self.staticon.set_visible(False)
        gtk.main_quit()


class MainApp:

    def __init__(self):
        self.ctrl = Controller(os.path.join('project', 'config.yml'))

    def start(self):
        self.statusicon = StatusIcc(self)

if __name__ == "__main__":
    app = MainApp()
    app.start()
