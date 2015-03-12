#!/usr/bin/env python2.7

# -*- coding: utf-8 -*-
import urllib2,sys,time,os,lispeak,json,dbus,dbus.service,getpass
from HTMLParser import HTMLParser
from PIL import Image
import os.path
import cStringIO

from gi.repository import Gtk
from gi.repository import Gdk as gdk
from gi.repository import GdkPixbuf as pixbuf
from gi.repository import Gtk as gtk
from gi.repository import GObject as gobject

FILEFOLDER="/tmp/lispeak_" + getpass.getuser()

#ar = lispeak.getSingleInfo("ARDUINO")
#if ar == "":
#    ar = '/dev/ttyACM1'
#    lispeak.writeSingleInfo('ARDUINO','/dev/ttyACM1')
#lcd = lispeak.arduino(lispeak.getSingleInfo("ARDUINO"))
#lcd.sendText("Welcome|LiSpeak LCD;")

preInfo = lispeak.getInfo()
if "NOTIFICATIONS" not in preInfo:
    lispeak.writeSingleInfo("NOTIFICATIONS","LiSpeak")
if "NOTIFYX" not in preInfo:
    lispeak.writeSingleInfo("NOTIFYX","50")
if "NOTIFYY" not in preInfo:
    lispeak.writeSingleInfo("NOTIFYY","50")
if "MESSAGES" not in preInfo:
    lispeak.writeSingleInfo("MESSAGES","False")


try:
    os.chdir("Microphone")
except:
    print "Currently in",os.getcwd()

try:
    from dbus.mainloop.glib import DBusGMainLoop
except ImportError:
    from dbus.mainloop.qt.DBusQtMainLoop import DBusGMainLoop
    #if none exists, an ImportError will be throw
DBusGMainLoop(set_as_default=True)

def getAvgColB():
    try:
        f = os.popen("gsettings get org.gnome.desktop.background picture-uri")
        f = f.read().replace("\n","").replace("'","").replace("file://","")
        img = Image.open(cStringIO.StringIO(open(f).read()))
        width, height = img.size
        pixels = img.load()  
        sides = [pixels[x,y] for x in range(3)+range(width-3,width) for y in range(height)]
        topbottom = [pixels[x,y] for x in range(3,width-3) for y in range(3) + range(height-3,height)]
        borderPixels = sides + topbottom
        rsum = 0
        gsum = 0
        bsum = 0
        for r,g,b in borderPixels:
            rsum = rsum + r
            gsum = gsum + g
            bsum = bsum + b
        numPixs = len(borderPixels)
        rAvg = rsum / numPixs
        gAvg = gsum / numPixs
        bAvg = bsum / numPixs
        bright = ((rAvg * 299) + (gAvg * 587) + (bAvg * 114)) / 1000
        if bright > 100:
            bright = "black"
        else:
            bright = "white"
        return '#%02x%02x%02x' % (rAvg,gAvg,bAvg),bright
    except:
        return "#4D65F0","black"

class MyDBUSService(dbus.service.Object):
    """ This is a service that waits for somebody call create_notification(data) """
    def __init__(self):
        global gbus
        bus_name = dbus.service.BusName('com.bmandesigns.lispeak.notify', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/com/bmandesigns/lispeak/notify')

    @dbus.service.method('com.bmandesigns.lispeak.notify')
    def create_notification(self, data):
        try:
            popup.queue.append(data)
        except:
            pass
            
    @dbus.service.method('com.bmandesigns.lispeak.notify')
    def new_command(self, speech, command):
        self.CommandRecognized(speech, command)

    @dbus.service.method('com.bmandesigns.lispeak.notify')
    def Quit(self):
        """Removes this object from the DBUS connection and exits"""
        self.remove_from_connection()
        Gtk.main_quit()
        return
        
    @dbus.service.signal('com.bmandesigns.lispeak.notify')
    def CommandRecognized(self, speech, command):
        #return str(speech), str(command) #fails if there are non-ascii characters
        return speech.encode('utf-8'),command.encode('utf-8')

        
MyDBUSService()

def notify(summary, body='', app_name='LiSpeak', app_icon='',
            timeout=5000, actions=[], hints=[], replaces_id=0):
        _bus_name = 'org.freedesktop.Notifications'
        _object_path = '/org/freedesktop/Notifications'
        _interface_name = _bus_name

        session_bus = dbus.SessionBus()
        obj = session_bus.get_object(_bus_name, _object_path)
        interface = dbus.Interface(obj, _interface_name)
        interface.Notify(app_name, replaces_id, app_icon,
                summary, body, actions, hints, timeout)

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if len(attrs) > 0:
            self.data[tag] = {}
            for a in attrs:
                self.data[tag][a[0]] = a[1] 
class PopUp:
    def __init__(self):
        filename = "../Setup/templates/popup.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(filename)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window1")
        self.title = self.builder.get_object("lblTitle")
        self.message = self.builder.get_object("lblMessage")
        self.titleBox = self.builder.get_object("labelbox")
        self.titleBox.connect("button-release-event", self.on_clicked)
        self.exit = self.builder.get_object("exitbox")
        self.exit.connect("button-release-event",self.close_notify)
        self.icon = self.builder.get_object("imgIcon") 
        self.window.set_gravity(gdk.Gravity.NORTH_WEST)  
        self.display = False
        self.window.set_keep_above(True)
        self.counter = 0
        self.counter2 = 0
        self.counting = False
        self.queue = []
        
        self.info = lispeak.getInfo()

        gobject.timeout_add_seconds(1, self.timer)
        try:
            gobject.timeout_add_seconds(0.2, self.display_notify)
        except:
            print "Reverting to 1 second check"
            gobject.timeout_add_seconds(1, self.display_notify)       
        gobject.timeout_add_seconds(30, self.message_system)
        while gtk.events_pending():
            gtk.main_iteration_do(True)
        self.message_system()
            
    def speak(self,a=None,b=None,c=None):
        lispeak.speak(self.speech)
        return False

    def close_notify(self,a=None,b=None,c=None):
        print "Closing"
        for each in range(10,-1,-1):
            self.window.set_opacity(float("0."+str(each)))
            while gtk.events_pending():
                gtk.main_iteration_do(True)
            time.sleep(0.05)
        self.display = False
        self.window.hide()
        self.counting = False
            
    def on_clicked(self, widget, thrid):
        if self.counting:
            self.counting = False   
            self.window.set_opacity(1.0)
        else:
            self.counting = True
            self.window.set_opacity(0.9)
        
    def message_system(self):
        if self.info['MESSAGES'] == "True":
            f = urllib2.urlopen("http://lispeak.bmandesigns.com/functions.php?f=messageUpdate")
            text = f.read()
            message = json.loads(text.replace('\r', '\\r').replace('\n', '\\n'),strict=False)
            lastId = lispeak.getSingleInfo("lastid")
            if lastId == "":
                lastId = message['id']
            try:
                go = int(message['id']) > int(lastId)
            except:
                go = True
            if go:
                if 'icon' in message:
                    urllib.urlretrieve(message['icon'], "/tmp/lsicon.png")
                    self.queue.append({'title':"LiSpeak - "+message['title'],'message':message['text'],'icon':"/tmp/lsicon.png","speech":message['text']})
                else:
                    self.queue.append({'title':"LiSpeak - "+message['title'],'message':message['text'],"speech":message['text']})
            
            lispeak.writeSingleInfo("lastid",str(int(message['id'])))
        return True
        
    def display_notify(self):
         if os.path.exists(FILEFOLDER + "/notification.lmf"):
             print "Notification"
             time.sleep(0.05)
             with open(FILEFOLDER + "/notification.lmf") as f:
                 data = lispeak.parseData(f.read())
                 self.queue.append(data)
             os.remove(FILEFOLDER + "/notification.lmf")
         return True
         
 
    def timer(self):
        color = gdk.color_parse(getAvgColB()[0])
        color2 = gdk.color_parse(getAvgColB()[1])
        for wid in [self.window,self.exit,self.titleBox]:
            wid.modify_bg(Gtk.StateFlags.NORMAL, color)
        for wid in [self.title,self.message]:
            wid.modify_fg(Gtk.StateFlags.NORMAL, color2)
        try:
            if self.info['NOTIFICATIONS'] == "LiSpeak":
                if self.counting:
                    if self.counter == 0:
                        self.display = True
                        for each in range(0,10):
                            if self.counting:
                                self.window.set_opacity(float("0."+str(each)))
                                while gtk.events_pending():
                                    gtk.main_iteration_do(True)
                                self.window.show_all()
                                self.window.move(int(self.info['NOTIFYX']),int(self.info['NOTIFYY']))
                                self.icon.set_visible(not self.image_hide)
                        self.speak(self.speech)
                    if self.counter == 5:
                        if self.window.get_opacity() != 0.0:
                            for each in range(9,-1,-1):
                                self.window.set_opacity(float("0."+str(each)))
                                while gtk.events_pending():
                                    gtk.main_iteration_do(True)
                                time.sleep(0.02)
                            self.window.hide()
                            self.display = False
                            self.counting = False
                    self.counter += 1
            if not self.counting and len(self.queue) > 0 and self.display == False:
                data = self.queue[0]
                try:
                    self.message.set_text("")
                    self.message.set_text(data['message'].replace("\\n","\n"))
                except:
                    pass
                self.title.set_text(data['title'])
                if 'icon' in data:
                    if data['icon'].startswith("http"):
                        f2 = urllib2.urlopen(data['icon'])
                        output = open('/tmp/lispeak-image','wb')
                        output.write(f2.read())
                        output.close()
                        buf = pixbuf.Pixbuf.new_from_file_at_size("/tmp/lispeak-image",75,75)
                        self.icon.set_from_pixbuf(buf)
                    else:
                        try:
                            buf = pixbuf.Pixbuf.new_from_file_at_size(data['icon'].replace("file://",""),75,75)
                            self.icon.set_from_pixbuf(buf)
                        except:
                            print "Invalid Image:",data['icon']
                    self.image_hide = False
                else:
                    self.image_hide = True
                if "speech" in data:
                    print data['speech']
                    if data["speech"] != True:
                        self.speech = data['speech']
                    else:
                        self.speech = data['title']
                else:
                    self.speech = data['title']
                if self.info['NOTIFICATIONS'] == "LiSpeak":
                    self.counter = 0
                    self.counting = True
                elif self.info['NOTIFICATIONS'] == "System":
                    try:
                        if "icon" in data:
                            if data['icon'].startswith("http"):
                                f2 = urllib2.urlopen(data['icon'])
                                output = open('/tmp/lispeak-image','wb')
                                output.write(f2.read())
                                output.close()
                                notify(summary=data['title'],body=data['message'].replace("\\n","\n"),app_icon='/tmp/lispeak-image')
                            else:
                                notify(summary=data['title'],body=data['message'].replace("\\n","\n"),app_icon=data['icon'])
                        else:
                            notify(summary=data['title'],body=data['message'].replace("\\n","\n"))
                    except:
                        notify(summary=data['title'])
                    self.speak(self.speech)
                self.queue.pop(0)
                #lcd.sendText(self.title.get_text()+"|"+self.message.get_text()+";")
            return True
        except:
            print "AN ERROR OCCURED!", sys.exc_info()
            return True
        


popup = PopUp()
Gtk.main()

