#!/usr/bin/env python2.7

#
# Usage: recognized <speech> <command>
# Alert other program/plugin what speech has been recognized and which command is going to be executed
#

import dbus,sys

try:
    from dbus.mainloop.glib import DBusGMainLoop
except ImportError:
    from dbus.mainloop.qt.DBusQtMainLoop import DBusGMainLoop
    #if none exists, an ImportError will be throw
DBusGMainLoop(set_as_default=True)
bus = None

if bus == None:
    bus = dbus.SessionBus()
proxy_obj = bus.get_object("com.bmandesigns.lispeak.notify", "/com/bmandesigns/lispeak/notify")
proxy_iface = dbus.Interface(proxy_obj, "com.bmandesigns.lispeak.notify")
proxy_iface.new_command(sys.argv[1],sys.argv[2])
