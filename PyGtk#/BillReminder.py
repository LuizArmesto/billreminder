#!/usr/bin/python
#
# The MIT License
#
# Copyright (c) 2006 Og Maciel
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of 
# this software and associated documentation files (the "Software"), to deal in the 
# Software without restriction, including without limitation the rights to use, copy, 
# modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, 
# and to permit persons to whom the Software is furnished to do so, subject to the 
# following conditions:
#
# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION 
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import gtk, gtk.glade, gobject
import os
import threading


class Dialog:
    def __init__(self, name):
        self.glade = gtk.glade.XML('billreminder.glade', name)

        self.glade.signal_autoconnect({
        })
        
        self.glade.Modal = true;
        self.glade.Run();


class GtkClient:

    def __init__(self):
                
        self.glade = gtk.glade.XML('billreminder.glade', 'frmMenu')
	self.btnClose = self.glade.get_widget("btnClose")
	self.btnDisplay = self.glade.get_widget("btnDisplay")
	
        self.glade.signal_autoconnect({
            'on_btnClose_clicked' : self.on_btnClose_clicked,
            'on_btnDisplay_clicked' : self.on_btnDisplay_clicked
        })

    # Callbacks
    def on_btnClose_clicked(self, widget, data = None):
	gtk.main_quit()

    def on_btnDisplay_clicked(self, widget, data = None):
	Dialog("frmDisplay")

if __name__ == '__main__':
    gtk.threads_init()
    client = GtkClient()
    gtk.main()
