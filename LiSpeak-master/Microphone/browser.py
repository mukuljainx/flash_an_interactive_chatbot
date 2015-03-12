#!/usr/bin/env python2.7

from gi.repository import Gtk as gtk
from gi.repository import Gdk as gdk
from gi.repository import WebKit as webkit
from gi.repository import GObject as gobject

import lispeak

class Browser:
    default_site = "http://lispeak.bmandesigns.com/home?app=special"
    
    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def __init__(self):
        gobject.threads_init()
        self.window = gtk.Window()
        self.window.set_resizable(True)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_title("LiSpeak Plugin Browser")
        self.window.set_default_size(1000,800)

        self.web_view = webkit.WebView()
        self.web_view.open(self.default_site)

        self.web_view.connect("resource-request-starting", self.loading)

        scroll_window = gtk.ScrolledWindow(None, None)
        scroll_window.add(self.web_view)

        vbox = gtk.VBox(False, 0)
        vbox.add(scroll_window)

        self.window.add(vbox)
        self.window.show_all()

    def loading(self,web_view,web_frame,web_resource,request,response):
        url = request.get_uri()
        if url.startswith("http://lispeak.bmandesigns.com/functions.php?f=download&t=id&s="):
            pid = url.replace("http://lispeak.bmandesigns.com/functions.php?f=download&t=id&s=","")
            lispeak.downloadPackage(pid,"id")

    def on_active(self, widge, data=None):
        url = self.url_bar.get_text()
        try:
            url.index("://")
        except:
            url = "http://"+url
        self.web_view.open(url)

    def main(self):
        gtk.main()

if __name__ == "__main__":
    browser = Browser()
    browser.main()
