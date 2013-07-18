__author__ = 'Nikhil Ben Kuruvilla'

#!/usr/bin/env python
from gi.repository import Gtk
import sys
from gi.repository import AppIndicator3 as AppIndicator
import sqlite3 as lite
#from pypodio2 import api

import imaplib
import re
import os

PING_FREQUENCY = 10 # seconds


class PodioTaskApplet:
    def __init__(self):
        self.con = lite.connect('db/podio.sqlite3')
        self.working_dir = os.getcwd()
        self.ind = AppIndicator.Indicator.new("podio-task-indicator",
            self.working_dir +"/assets/podio.png",
            AppIndicator.IndicatorCategory.APPLICATION_STATUS)
        self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        self.ind.set_attention_icon(self.working_dir +"/assets/podio.png")

        self.menu_setup()
        self.ind.set_menu(self.menu)
        
        cur = self.con.cursor()    
        cur.execute("SELECT * from podio_user")
        
        rows = cur.fetchall()
        
        print len(rows)

#==============================================================================
#         c = api.OAuthClient(
#         client_id,
#         client_secret,
#         username,
#         password    
#         )
# 
# 
#         print c.Task.get_summary(limit = 10)
#==============================================================================
        
    def save_settings(self , dialog, *_args):
        cur = self.con.cursor()    
        # cur.execute("DELETE from podio_user")

        
        podio_email = self.glade.get_object("podio_email").get_text()
        podio_password = self.glade.get_object("podio_password").get_text()
        podio_client_id = self.glade.get_object("podio_client_id").get_text()
        podio_client_secret = self.glade.get_object("podio_client_secret").get_text()
        
        cur.execute("INSERT INTO podio_user VALUES ('"+podio_email+"','"+podio_password+"','"+podio_client_id+"','"+podio_client_secret+"');")
        print cur.lastrowid
       
       # self.window.hide()

    def menu_setup(self):
        self.menu = Gtk.Menu()

        # Separators
        sep_1 = Gtk.SeparatorMenuItem()
        sep_2 = Gtk.SeparatorMenuItem()

        # Sample Tasks
        self.task_1 = Gtk.MenuItem("Zendesk Salesforce Integration")
        self.task_2 = Gtk.MenuItem("Put up the time registration app")
        self.task_3 = Gtk.MenuItem("Please fix the web issue")

        self.task_1.show()
        self.task_2.show()
        self.task_3.show()

        self.menu.append(self.task_1)
        self.menu.append(self.task_2)
        self.menu.append(self.task_3)

        # Show separator
        sep_1.show()
        self.menu.append(sep_1)

        # Preferences
        self.pref_item = Gtk.MenuItem("Preferences")
        self.pref_item.connect("activate", self.preference_box)
        self.pref_item.show()
        self.menu.append(self.pref_item)

        # Help
        self.help_item = Gtk.MenuItem("Help")
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
      self.window.show() 



    def main(self):
        self.check_mail()
       # Gtk.timeout_add(PING_FREQUENCY * 1000, self.check_mail)
        Gtk.main()

    def quit(self, widget):
        sys.exit(0)
        
    def on_cancel_clicked(self, dialog, *_args):
        dialog.destroy()
        
    def check_mail(self):
        messages, unread = self.gmail_checker('email','pass')
        if unread > 0:
            self.ind.set_status(AppIndicator.IndicatorStatus.ATTENTION)
        else:
            self.ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)
        return True

    def gmail_checker(self, username, password):
        i = imaplib.IMAP4_SSL('imap.gmail.com')
        try:
            i.login(username, password)
            x, y = i.status('INBOX', '(MESSAGES UNSEEN)')
            messages = int(re.search('MESSAGES\s+(\d+)', y[0]).group(1))
            unseen = int(re.search('UNSEEN\s+(\d+)', y[0]).group(1))
            return (messages, unseen)
        except:
            return False, 0

if __name__ == "__main__":
    indicator = PodioTaskApplet()
    indicator.main()
    Gtk.main()
