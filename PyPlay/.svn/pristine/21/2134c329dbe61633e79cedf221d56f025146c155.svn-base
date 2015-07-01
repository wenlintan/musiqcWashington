
from collections import defaultdict
import pygtk, os, pickle
pygtk.require( '2.0' )

import gtk, pango
from gtk import glade

def get_fake( prefs ):
    return None

found_controllers = []
try:
    import winamp_controller
    found_controllers.append( winamp_controller.Controller )
except ImportError:
    found_controllers.append( get_fake )
    
import mpc_controller, wawi_controller
found_controllers.append( mpc_controller.Controller )
found_controllers.append( wawi_controller.Controller )

class Preferences:
    controllers = found_controllers
    media_players = { "Winamp": controllers[0],
                      "Media Player Classic": controllers[1],
                      "Winamp (Bad Boy)": controllers[2] }

    prefs = {
        "play_directory": "play",
        "download_directory": ".",
        "media_player": mpc_controller.Controller,
        "media_status_refresh": 1,
        "media_player_port": 13579,
        "shared_folders": {},
        "server_host": "localhost",
        "server_port": 4321,
        "auth_port": 4320,
        "client_port": 4322 }
    
    def __init__( self, filename, glade_file ):
        self.pref_callbacks = defaultdict( list )
        
        self.glade = glade_file
        self.glade.signal_autoconnect( self )
        self.set_widgets()
        
        self._shared_folders = gtk.ListStore( str, str )
        self._shared_folders_tree_view.set_model( self._shared_folders )
        
        self._names_col = gtk.TreeViewColumn( 'Names' )
        self._folders_col = gtk.TreeViewColumn( 'Folders' )
        self._shared_folders_tree_view.append_column( self._names_col )
        self._shared_folders_tree_view.append_column( self._folders_col )

        self._names_cell = gtk.CellRendererText()
        self._folders_cell = gtk.CellRendererText()
        
        self._names_col.pack_start( self._names_cell, True )
        self._folders_col.pack_start( self._folders_cell, True )

        self._names_col.set_attributes( self._names_cell, text=0 )
        self._folders_col.set_attributes( self._folders_cell, text=1 )

        self._preference_window.hide()

        # load initial preferences from file
        self.pref_filename = filename
        self.load_preferences()
        
    def set_widgets( self ):
        widgets = ("preference_window", "shared_folders_tree_view",
                   "play_dir_button", "download_dir_button",
                   "media_player_entry", "media_player_refresh_entry",
                   "media_player_port_entry",
                   "share_dir_name_entry", "share_dir_button",
                   "server_host_entry", "server_port_entry",
                   "auth_port_entry", "client_port_entry")
        
        gw = self.glade.get_widget
        for widgetName in widgets:
            setattr(self, "_" + widgetName, gw(widgetName))

    def on_preference_window_delete_event( self, widget, event, data = None ):
        self._preference_window.hide()
        return True

    def on_preferences_menu_activate( self, menuitem, data = None ):
        self.setup_preferences()
        self._preference_window.show()

    def on_preferences_ok_button_clicked( self, button, data = None ):
        self.extract_preferences()
        self.save_preferences()
        self._preference_window.hide()
        
    def on_preferences_cancel_button_clicked( self, button, data = None ):
        self._preference_window.hide()

    def on_add_share_dir_button_clicked( self, button, data = None ):
        d = self._share_dir_button.get_current_folder()
        name = self._share_dir_name_entry.get_text()
        print name, d

        def dialog( err ):
            md = gtk.MessageDialog
            self.message = md( self._preference_window,
                gtk.DIALOG_DESTROY_WITH_PARENT, gtk.MESSAGE_ERROR,
                gtk.BUTTONS_OK, err )
            
        if not name:
            dialog( "No name given for shared folder." )
            return

        if not os.path.isdir( d ):
            dialog( "Invalid shared folder." )
            return
            
        self._shared_folders.append( (name,d) )

    def on_remove_share_dir_button_clicked( self, button, data = None ):
        sel = self._shared_folders_tree_view.get_selection()
        model, it = sel.get_selected()
        model.remove( it )

    def set( self, name, value ):
        self.prefs[ name ] = value

        # for media player actually create object to invoke callback
        if name == "media_player":
            value = value( self )
            
        for cb in self.pref_callbacks[ name ]:
            cb( name, value )

    def get( self, name ):
        return self.prefs[name]

    def subscribe( self, name, cb ):
        self.pref_callbacks[ name ].append( cb )

        if name == "media_player":
            cb( name, self.prefs[name](self) )
            return
        cb( name, self.prefs[name] )

    def load_preferences( self ):
        try:
            pfile = file( self.pref_filename, 'r' )
            self.prefs = pickle.load( pfile )
            pfile.close()
                
        except IOError, EOFError:
            pass            

    def save_preferences( self ):
        pfile = file( self.pref_filename, 'w' )
        pickle.dump( self.prefs, pfile )
        pfile.close()

    def extract_preferences( self ):
        play_dir = self._play_dir_button.get_current_folder()
        down_dir = self._download_dir_button.get_current_folder()

        self.set( "play_directory", play_dir )
        self.set( "download_directory", down_dir )

        model = self._media_player_entry.get_model()
        it = self._media_player_entry.get_active_iter()
        if it is not None:  media_name = model.get_value( it, 0 )
        else:               media_name = "Media Player Classic"

        self.set( "media_player", self.media_players[media_name] )

        media_refresh = self._media_player_refresh_entry.get_text()
        self.set( "media_status_refresh", media_refresh )

        media_port = self._media_player_port_entry.get_value_as_int()
        self.set( "media_player_port", media_port )

        shared_folders = {}
        it = self._shared_folders.get_iter_first()
        while it is not None:
            name = self._shared_folders.get_value( it, 0 )
            folder = self._shared_folders.get_value( it, 1 )
            shared_folders[ name ] = folder

            it = self._shared_folders.iter_next( it )
        self.set( "shared_folders", shared_folders )

        shost = self._server_host_entry.get_text()
        sport = self._server_port_entry.get_value_as_int()

        self.set( "server_host", shost )
        self.set( "server_port", int(sport) )

        aport = self._auth_port_entry.get_value_as_int()
        cport = self._client_port_entry.get_value_as_int()

        self.set( "auth_port", int(aport) )
        self.set( "client_port", int(cport) )
        print self.prefs

        
    def setup_preferences( self ):
        if "play_directory" in self.prefs:
            path = os.path.realpath( self.prefs["play_directory"] )
            self._play_dir_button.set_current_folder( path )

        if "download_directory" in self.prefs:
            path = os.path.realpath( self.prefs["download_directory"] )
            self._download_dir_button.set_current_folder( path )

        if "media_player" in self.prefs:
            c = self.prefs[ "media_player" ]
            self._media_player_entry.set_active( self.controllers.index(c) )

        if "media_status_refresh" in self.prefs:
            refr = self.prefs[ "media_status_refresh" ]
            self._media_player_refresh_entry.set_text( str( refr ) )

        if "media_player_port" in self.prefs:
            port = self.prefs[ "media_player_port" ]
            self._media_player_port_entry.set_value( port )
            
        self._shared_folders.clear()
        if "shared_folders" in self.prefs:
            for name, folder in self.prefs[ "shared_folders" ].items():
                self._shared_folders.append( (name, folder) )

        if "server_host" in self.prefs:
            self._server_host_entry.set_text( self.prefs["server_host"] )

        if "server_port" in self.prefs:
            self._server_port_entry.set_value( self.prefs["server_port"] )

        if "auth_port" in self.prefs:
            self._auth_port_entry.set_value( self.prefs["auth_port"] )

        if "client_port" in self.prefs:
            self._client_port_entry.set_value( self.prefs["client_port"] )

            

    
            
