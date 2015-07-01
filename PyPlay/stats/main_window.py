
import pygtk
pygtk.require('2.0')
import gtk

import sys, string
import section

import util_window
from util_window import *

class tab:
    def __init__( self, name, notebook ):
        self.vbox = gtk.VBox()
        self.name = gtk.Label( name )
        notebook.append_page( self.vbox, self.name )
        notebook.show_all()
        
        self.section = section.section(self.vbox)

    def add_variable( self, name, data ):
        self.section.add_variable( name, data )

    def graph_variables( self, var1, var2 ):
        self.section.graph_variables( var1, var2 )

class window:
    def delete_event( self, widget, event, data=None ):
        gtk.main_quit()
        return False

    def add_tab( self, name ):
        self.tabs.append( tab( name, self.notebook ) )

    def add_variable( self, name, data ):
        page = self.notebook.get_current_page()
        self.tabs[ page ].add_variable( name, data )

    def graph_variables( self, var1, var2 ):
        page = self.notebook.get_current_page()
        self.tabs[ page ].graph_variables( var1, var2 )

    def __init__( self ):

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title("AnalStat")
        self.window.set_size_request(600, 250)

        self.window.connect("delete_event", self.delete_event)
        self.window.set_border_width(10)

        self.main_vert = gtk.VBox()
        self.menu_hort = gtk.HBox()
        self.main_vert.pack_start( self.menu_hort, False )

        util_window.default_window = self.window
        self.add_tab_button = gtk.Button( "Add Section" )
        self.add_tab_button.connect( "clicked", create_section_dialog, self )
        self.menu_hort.pack_start( self.add_tab_button, False )

        self.add_var_button = gtk.Button( "Add Variable" )
        self.add_var_button.connect( "clicked", create_variable_dialog, self )
        self.menu_hort.pack_start( self.add_var_button, False )

        self.graph_button = gtk.Button( "Graph Variables" )
        self.graph_button.connect( "clicked", create_graph_dialog, self )
        self.menu_hort.pack_start( self.graph_button, False )
        
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos( gtk.POS_LEFT )
        self.main_vert.pack_start( self.notebook )
        
        self.window.add( self.main_vert )
        
        self.tabs = [ tab( "Default", self.notebook ) ]
        self.window.show_all()

    def run( self ):
        gtk.main()
