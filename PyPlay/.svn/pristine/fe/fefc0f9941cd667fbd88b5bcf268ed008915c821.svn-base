
import pygtk
pygtk.require('2.0')
import gtk, pango


class prompt:

    def cb( self, widget, ok = None ):
        if ok: self.ok_callback( *[ v.get_text() for v in self.vars ] )
        self.dialog.destroy()
        
    def __init__( self, main, title, ok_callback ):

        self.dialog = gtk.Dialog( title, main, gtk.DIALOG_MODAL )
        self.ok_callback = ok_callback

        self.ok = gtk.Button( "OK" )
        self.cancel = gtk.Button( "Cancel" )
        self.ok.connect( "clicked", self.cb, True )
        self.cancel.connect( "clicked", self.cb, False )
        
        self.dialog.action_area.pack_start( self.ok )
        self.dialog.action_area.pack_start( self.cancel )

        self.dialog.show_all()

    def make_text_prompt( self, prompt, entry_names ):
        l = gtk.Label( prompt )
        self.dialog.vbox.pack_start( l )

        self.vars = []
        self.table = gtk.Table( len(entry_names), 2 )
        for i, name in enumerate( entry_names ):
            e = gtk.Entry()
            if not i:   e.grab_focus()
            
            e.modify_font(pango.FontDescription('monospace 10'))
            self.vars.append( e )

            self.table.attach( gtk.Label( name + ": " ), 0, 1, i, i+1 )
            self.table.attach( e, 1, 2, i, i+1 )
        self.dialog.vbox.pack_start( self.table )
        self.dialog.vbox.show_all()
        
default_window = None
def create_section_dialog( widget, main_window = None ):
    tp = prompt(  main_window.window, "Add Section", main_window.add_tab )
    tp.make_text_prompt( "Choose section name:\n", [ "Name" ] )

def create_variable_dialog( widget, main_window = None ):
    tp = prompt(  main_window.window, "Add Variable to Section",
                  main_window.add_variable )
    
    varprompt = """
Choose variable name and specify data:
Example data:
    1.57
    1.09 \ 1.5398 \ 90.2
    x , y -> x*sin(y)
"""
    tp.make_text_prompt( varprompt, [ "Name", "Data" ] )

def create_graph_dialog( widget, main_window = None ):
    tp = prompt( main_window.window, "Graph Variables",
                 main_window.graph_variables )

    varprompt = """
Choose names of variables to graph:
"""
    tp.make_text_prompt( varprompt, [ "X", "Y" ] )

def create_graph_desc_dialog( widget, main_window = None ):
    tp = prompt( main_window.window, "Graph Description",
                 main_window.set_graph_desc )
    varprompt = """
Choose title and axis labels for graph:
"""
    tp.make_text_prompt( varprompt, ["Title", "X Label", "Y Label"] )

def create_error_dialog( widget, varview = None ):
    tp = prompt( default_window, "Add Errors", varview.add_errors )
    varprompt = """
Choose errors for this data:
"""
    tp.make_text_prompt( varprompt, ["Err"] )
    pass
    
