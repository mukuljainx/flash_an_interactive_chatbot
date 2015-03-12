#!/usr/bin/env python2.7

#
# Applet in system tray
#

import gtk,gobject,os,appindicator,subprocess,lispeak,dbus

try:
    os.chdir("Microphone")
except:
    print "Currently in",os.getcwd()
PWD=str(os.getcwd())


try:
    from dbus.mainloop.glib import DBusGMainLoop
except ImportError:
    from dbus.mainloop.qt.DBusQtMainLoop import DBusGMainLoop
    #if none exists, an ImportError will be throw
DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()
bus.request_name("com.bmandesigns.lispeak.appStatus")

SIG_WAIT=1
SIG_DONE=2
SIG_STOP=3
SIG_RECORD=4
SIG_RESULT=5

last_signal=None

def msg_handler(*args,**keywords):
    global last_signal
    try:
        last_signal=int(keywords['path'].split("/")[4])
    except:
        pass

bus.add_signal_receiver(handler_function=msg_handler, dbus_interface='com.bmandesigns.lispeak', signal_name='AppStatus', interface_keyword='iface',  member_keyword='member', path_keyword='path')

class indicator:
    def __init__(self):
        
        self.ind = appindicator.Indicator("LiSpeak", PWD + "/Indicator/mic.png", appindicator.CATEGORY_APPLICATION_STATUS)
        self.ind.set_status(appindicator.STATUS_ACTIVE)

        self.menu_setup()
        self.ind.set_menu(self.menu)
        self.progress = 0
        
        gobject.timeout_add(100, self.callback)

    def menu_setup(self):
        self.menu = gtk.Menu()

        self.p_item = gtk.MenuItem("Install a Plugin")
        self.p_item.connect("activate", self.install)
        self.p_item.show()
        self.menu.append(self.p_item)
        
        self.p_item = gtk.MenuItem("Plugin Browser")
        self.p_item.connect("activate", self.openBrowser)
        self.p_item.show()
        self.menu.append(self.p_item)
        
        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)

        self.r_item = gtk.MenuItem("Restart Servers")
        self.r_item.connect("activate", self.restart)
        self.r_item.show()
        self.menu.append(self.r_item)
        
        self.r_item = gtk.MenuItem("Settings")
        self.r_item.connect("activate", self.settings)
        self.r_item.show()
        self.menu.append(self.r_item)
        
        separator = gtk.SeparatorMenuItem()
        separator.show()
        self.menu.append(separator)

        self.quit_item = gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)

    def main(self):
        gtk.main()

    def quit(self, widget):
        os.chdir("../")
        subprocess.call(["./stop"])
    
    def restart(self,widget):
        os.chdir("../")
        subprocess.call(["./start"])

    def install(self,widget):
        p = subprocess.Popen("zenity --entry --text='Enter the Plugin Name' --title='Plugin Installer'", shell=True, stdout=subprocess.PIPE).communicate()[0].replace('\n','')
        print "Installing: "+p
        #lispeak.downloadPackage(p)
        os.system("../lispeak -p "+p)
        
    def openBrowser(self,widget):
        os.system(PWD + "/../Recognition/bin/open "+PWD+"/browser.py")
        print "Opened Browser"
        
    def settings(self,widget):
        print PWD + "/../Recognition/bin/open "+PWD+"/settings.py"
        os.system(PWD + "/../Recognition/bin/open "+PWD+"/settings.py")
        print "Opened Settings"
        
    def callback(self):
        global last_signal
        reset = False
        if last_signal==SIG_DONE:
            self.ind.set_icon(PWD + "/Indicator/mic.png")
            last_signal = None
            reset = True
        if last_signal==SIG_RECORD:
            self.ind.set_icon(PWD + "/Indicator/listen.png")
            last_signal = None
            reset = True
        if last_signal==SIG_STOP:
            self.ind.set_icon(PWD + "/Indicator/wait.png")
            last_signal = None
            reset = True
        if reset == False and last_signal==SIG_WAIT:
            self.ind.set_icon(PWD + "/Indicator/analyzing/tmp-"+str(self.progress)+".gif")
            self.progress += 1
            if self.progress == 8:
                self.progress = 0
        else:
            last_signal = None
        return True
ind = indicator()
gtk.main()
