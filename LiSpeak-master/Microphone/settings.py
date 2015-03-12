#!/usr/bin/env python2.7
# -*- coding: utf-8 -*- 

from gi.repository import Gtk
import sys,os

try:
    os.chdir("Microphone")
except:
    print "Currently in",os.getcwd()

class PopUp:
    def __init__(self):
    
        self.languages = {"English":"en","Polski":'pl',"Español":'es',"Français":'fr',"Italiano":"it"}
        self.languages2 = ["English","Polski","Español","Français","Italiano"]
        self.notifications = ["LiSpeak","System"]
    
        filename = "../Setup/templates/settings.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(filename)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("window1")
        self.window.set_title("LiSpeak Settings")
        self.about = self.builder.get_object("aboutdialog1")
        self.aboutBtn = self.builder.get_object("btnAbout")
        self.aboutBtn.connect("clicked", self.aboutOpen)
        self.notebook = self.builder.get_object("notebook1")
        self.exit = self.builder.get_object("btnClose")
        self.exit.connect("button-release-event",self.close)
        try:
            self.addItems(self.builder.get_object("cmbEngine"),["espeak","Google TTS","pico2wave"])
            self.addItems(self.builder.get_object("cmbLang"),self.languages2)
            self.addItems(self.builder.get_object("cmbNotifications"),self.notifications)
            self.fillFields(lispeak.getInfo())
            self.window.show_all()
        except KeyError:
            print "LiSpeak needs to be setup first"
            Gtk.main_quit()
    def close(self,a=None,b=None,c=None):
        self.userinfo = {}
        self.userinfo["AUTOSTART"] = str(self.builder.get_object("chkStart").get_active())
        self.userinfo["MESSAGES"] = str(self.builder.get_object("chkMessage").get_active())
        self.userinfo["UPDATES"] = self.builder.get_object("chkUpdates").get_active()
        self.userinfo["PROXY"] = str(self.builder.get_object("chkProxy").get_active())
        self.userinfo["PROXYHOST"] = self.builder.get_object("txtProxyhost").get_text()
        self.userinfo["PROXYPORT"] = self.builder.get_object("txtProxyport").get_text()
        self.userinfo["TTS"] = str(self.builder.get_object("chkTTS").get_active())
        self.userinfo["TTSENGINE"] = str(self.builder.get_object("cmbEngine").get_active_text())
        self.userinfo['LANG'] = self.languages[str(self.builder.get_object("cmbLang").get_active_text())]
        self.userinfo['CONTINUE'] = str(self.builder.get_object("chkContinue").get_active())
        self.userinfo['NOTIFICATIONS'] = str(self.builder.get_object("cmbNotifications").get_active_text())
        lispeak.writeInfo(self.userinfo)
        if self.userinfo["AUTOSTART"] == "True":
            lispeak.autostart(True)
        else:
            lispeak.autostart(False)
        if self.userinfo["CONTINUE"] == "True":
            lispeak.continuous(True)
        else:
            lispeak.continuous(False)
        Gtk.main_quit()
        os.system("../start")
    def aboutOpen(self,widget):
        self.about.show_all()
    def set_combo_active_text(self,combo, text):
        model = combo.get_model()
        for i in range(len(model)):
            if model[i][0] == text:
                combo.set_active(i)
    def addItems(self,obj,items):
        for e in items:
            obj.append_text(e)
    def fillFields(self, userinfo):
        for e in ['proxyport','proxyhost']:
            if e.upper() in userinfo:
                self.builder.get_object('txt'+e[0].upper()+e[1:]).set_text(userinfo[e.upper()])
        if "AUTOSTART" in userinfo:
            self.builder.get_object("chkStart").set_active(userinfo["AUTOSTART"] == "True")
        if "MESSAGES" in userinfo:
            self.builder.get_object("chkMessage").set_active(userinfo["MESSAGES"] == "True")
        if "UPDATES" in userinfo:
            self.builder.get_object("chkUpdates").set_active(userinfo["UPDATES"] == "True")
        if "PROXY" in userinfo:
            self.builder.get_object("chkProxy").set_active(userinfo["PROXY"] == "True")
        if "CONTINUE" in userinfo:
            self.builder.get_object("chkContinue").set_active(userinfo["CONTINUE"] == "True")
        if "TTS" in userinfo:
            self.builder.get_object("chkTTS").set_active(userinfo["TTS"] == "True")
        if "TTSENGINE" in userinfo:
            self.set_combo_active_text(self.builder.get_object("cmbEngine"), userinfo["TTSENGINE"])
        else:
            self.builder.get_object("cmbEngine").set_active(0)
        if "NOTIFICATIONS" in userinfo:
            self.set_combo_active_text(self.builder.get_object("cmbNotifications"), userinfo["NOTIFICATIONS"])
        else:
            self.builder.get_object("cmbNotifications").set_active(0)
        if "LANG" in userinfo:
            languages_back = {"en":"English","pl":"Polski",'es':'Español','fr':'Français',"it":"Italiano"}
            self.set_combo_active_text(self.builder.get_object("cmbLang"), languages_back[userinfo["LANG"]])
        else:
            self.builder.get_object("cmbLang").set_active(0)
        
try:
    import lispeak
except KeyError:
    print "LiSpeak needs to be setup first"
    sys.exit(1)
    
popup = PopUp()
Gtk.main()
