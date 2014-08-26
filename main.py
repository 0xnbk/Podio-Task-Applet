__author__ = 'Nikhil Ben Kuruvilla'

#!/usr/bin/env python
from gi.repository import Gtk
from gi.repository import GLib
import sys
from gi.repository import AppIndicator3 as AppIndicator
import sqlite3 as lite
from pypodio2 import api
import webbrowser

import os

PING_FREQUENCY = 60 # seconds

class PodioTaskApplet:
    def __init__(self):
        self.con = lite.connect('db/podio.sqlite3', isolation_level=None)
        self.working_dir = os.getcwd()
        self.ind = AppIndicator.Indicator.new("podio-task-indicator",
            self.working_dir +"/assets/podio_grey.png",
            AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        
        self.refresh = "false"
       
        self.menu_setup()
       
    def save_settings(self , dialog, *_args):
        db = self.con.cursor()    
        db.execute("DELETE from podio_user")
        
        podio_email = self.glade.get_object("podio_email").get_text()
        podio_password = self.glade.get_object("podio_password").get_text()
        podio_client_id = self.glade.get_object("podio_client_id").get_text()
        podio_client_secret = self.glade.get_object("podio_client_secret").get_text()
        
        db.execute("INSERT INTO podio_user(user_email, user_password, client_id, client_secret) VALUES ('"+podio_email+"','"+podio_password+"','"+podio_client_id+"','"+podio_client_secret+"');")
        db.close()
       
        self.window.hide()
        self.menu_setup()
        
    def list_task (self):
        
        self.menu = Gtk.Menu()
           
        db = self.con.cursor()    
        db.execute("SELECT * from podio_user")
        
        rows = db.fetchone()
  
        if len(rows) > 0:

            self.client_id = rows[2]
            self.client_secret = rows[3]
            self.username = rows[0]
            self.password = rows[1]
        
            c = api.OAuthClient(
                self.client_id,
                self.client_secret,
                self.username,
                self.password,    
            )
        
         
            task = c.Task.get_summary(limit = 50)
            overdue = 0
            
    
            if "overdue" in task and task["overdue"]["total"] > 0:
                
                #Change app icon
                 
                self.ind.set_attention_icon(self.working_dir +"/assets/podio_red.png")
                self.ind.set_status(AppIndicator.IndicatorStatus.ATTENTION)
                
                overdue = 1
                
                self.build_task_items(task["overdue"]["tasks"])
                 
            if "today" in task and task["today"]["total"] > 0:
    
                if overdue == 0:                
                    
                    #Change app icon
                     
                    self.ind.set_attention_icon(self.working_dir +"/assets/podio.png")
                    self.ind.set_status(AppIndicator.IndicatorStatus.ATTENTION)                
                
                self.build_task_items(task["today"]["tasks"])
                     
                     
            if "upcoming" in task:
           
                self.build_task_items(task["upcoming"]["tasks"])
                
            if "other" in task:
                
                self.build_task_items(task["other"]["tasks"])
                       
    def build_task_items (self, data) :
        for item in data:
            text = self.cap(item["text"], 40)
            show_task = Gtk.MenuItem(text)
            link = item["link"]
            show_task.connect("activate", self.open_task, link)
            show_task.show()
            self.menu.append(show_task)

    def menu_setup(self):
        
        print "Inside menu_setup"
        
        if self.refresh == "false":        
            GLib.timeout_add(PING_FREQUENCY * 1000, self.menu_setup)
            
        self.refresh = "false"
            
        self.menu = Gtk.Menu()
        
        try :        
            self.list_task()
        except:
            try_connect = Gtk.MenuItem("Connecting to Podio, please wait...")
            
            try_connect.show()
            try_connect.set_sensitive(False)
            self.menu.append(try_connect)

        # Separators
        sep_1 = Gtk.SeparatorMenuItem()
        sep_2 = Gtk.SeparatorMenuItem()

        # Show separator
        sep_1.show()
        self.menu.append(sep_1)
        
        # Refresh
        self.refresh_item = Gtk.MenuItem("Refresh")
        self.refresh_item.connect("activate", self.refresh_task)
        self.refresh_item.show()
        self.menu.append(self.refresh_item)

        # Preferences
        self.pref_item = Gtk.MenuItem("Preferences")
        self.pref_item.connect("activate", self.preference_box)
        self.pref_item.show()
        self.menu.append(self.pref_item)

        # Help
        self.help_item = Gtk.MenuItem("Help")
        self.help_item.connect("activate", self.open_help)
        self.help_item.show()
        self.menu.append(self.help_item)

        # About
        self.about_item = Gtk.MenuItem("About")
        self.about_item.connect("activate", self.open_about_item)
        self.about_item.show()
        self.menu.append(self.about_item)
        

        # Show separator
        sep_2.show()
        self.menu.append(sep_2)

        # Quit
        self.quit_item = Gtk.MenuItem("Quit")
        self.quit_item.connect("activate", self.quit)
        self.quit_item.show()
        self.menu.append(self.quit_item)   
        
        self.ind.set_menu(self.menu)
      
    def open_about_item(self, widget) :
        
      self.gladefile = "ui/about_box.glade"  
      self.glade = Gtk.Builder()
      self.glade.add_from_file(self.gladefile)
      self.glade.connect_signals(self)
      self.glade.get_object("podio_task_applet").show()
      
    def preference_box(self, widget) :
      self.gladefile = "ui/preference.glade"  
      self.glade = Gtk.Builder()
      self.glade.add_from_file(self.gladefile)
      self.glade.connect_signals(self)
      self.window = self.glade.get_object("preference_box")
      
      # Populate values from DB
      podio_email = self.glade.get_object("podio_email")
      podio_password = self.glade.get_object("podio_password")
      podio_client_id = self.glade.get_object("podio_client_id")
      podio_client_secret = self.glade.get_object("podio_client_secret")
      
      podio_email.set_text(self.username)
      podio_password.set_text(self.password)
      podio_client_id.set_text(self.client_id)
      podio_client_secret.set_text(self.client_secret)

      self.window.show() 
      
    def cap(self, s, l):
        return s if len(s)<=l else s[0:l-3]+'...'

    def quit(self, widget):
        sys.exit(0)
        
    def refresh_task(self, widget):
        self.refresh = "true"
        self.menu_setup()

        
    def on_cancel_clicked(self, dialog, *_args):
        dialog.destroy()
        
    def open_help(self, widget):
        webbrowser.open('http://podio.nikhilben.com/task-applet/help')
        
    def open_task(self, widget, *data):
        webbrowser.open(data[0])
        
if __name__ == "__main__":
    indicator = PodioTaskApplet()
    Gtk.main()


        #
        # connecting = self.menu.addAction("Connecting to Podio")
        # connecting.setDisabled(True)
        # connecting.triggered.connect(self.signin_view)