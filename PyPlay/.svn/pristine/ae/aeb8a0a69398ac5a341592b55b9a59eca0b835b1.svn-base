
from twisted.internet import gtk2reactor
gtk2reactor.install()

import pygtk
pygtk.require("2.0")

import gtk, pango
from gtk import glade
from twisted.internet import reactor, defer

from reality import *
from perception import *

##from knowledge import *
##from parser import *
from preferences import *

class MainWindow:
    def __init__( self ):
        self.downloads = {}
        self.file_iters = {}

        # Load interface from glade XML file
        self.glade = glade.XML( "talk.glade" )
        self.glade.signal_autoconnect( self )
        self.set_widgets()

    def set_widgets(self):
        widgets = ("main_window", "search_text_entry",
                   "file_tree_view", "status_label",
                   "download_window", "download_tree_view")
        
        gw = self.glade.get_widget
        for widgetName in widgets:
            setattr(self, "_" + widgetName, gw(widgetName))

        

mw = MainWindow()
reactor.run()
