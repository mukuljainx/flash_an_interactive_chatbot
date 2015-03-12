#!/usr/bin/env python2.7
"""Run this to see all commands that go through LiSpeak
"""
import gobject
import dbus
import dbus.service
import dbus.mainloop.glib


def on_mediakey(data,data2):
    print data
    print data2
    print

# set up the glib main loop.
dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.Bus(dbus.Bus.TYPE_SESSION)
bus_object = bus.get_object('com.bmandesigns.lispeak.notify','/com/bmandesigns/lispeak/notify')

# connect_to_signal registers our callback function.
bus_object.connect_to_signal('CommandRecognized', on_mediakey)

# and we start the main loop.
mainloop = gobject.MainLoop()
mainloop.run()
