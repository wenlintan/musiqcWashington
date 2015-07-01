
import pygtk
pygtk.require('2.0')
import gtk, pango

import variable
import graph_window
import dependency

class section:

    def add_variable( self, name, data ):

        if name in self.variable_map.keys():
            print "Variable '%s' already defined." % name
            return False
        
        var = variable.variable.parse( name, data )        
        if var is None:
            print "Variable failed to parse!"
            return False

        self.variable_map[ name ] = var
        varview = variable.variable_viewer( self.store, self.dep_graph, var )
        self.variables.append( (var, varview) )

    def graph_variables( self, var1, var2 ):
        graph_window.window( self.variable_map[var1], self.variable_map[var2] )

    def __init__( self, vbox ):
        self.variables = []
        self.variable_map = {}
        self.dep_graph = dependency.graph( )

        self.scroller = gtk.ScrolledWindow()
        self.store = gtk.TreeStore( str, str, str )

        self.tv = gtk.TreeView( self.store )
        self.tv.modify_font(pango.FontDescription('monospace 10'))

        vbox.pack_start( self.scroller )
        self.scroller.add( self.tv )
        
        self.tv.column = [None]*3
        self.name_col = gtk.TreeViewColumn( 'Name' )
        self.type_col = gtk.TreeViewColumn( 'Type' )
        self.data_col = gtk.TreeViewColumn( 'Data' )
        self.cols = [ self.name_col, self.type_col, self.data_col ]

        for col in self.cols:
            self.tv.append_column( col )

        self.name_cell = gtk.CellRendererText()
        self.type_cell = gtk.CellRendererText()
        self.data_cell = gtk.CellRendererText()
        
        self.cells = [ self.name_cell, self.type_cell, self.data_cell ]
        for i, cell in enumerate( self.cells ):
            self.cols[ i ].pack_start( cell, True )
            self.cols[ i ].set_attributes( cell, text=i )

        self.tv.set_search_column( 0 )
        self.name_col.set_sort_column_id( 0 )

        self.tv.connect( "button_press_event", self.tv_button_press, None )


    def tv_button_press( self, treeview, event, data = None ):

        if event.button == 3:
            
            time = event.time
            pthinfo = self.tv.get_path_at_pos(int(event.x),int(event.y))
            
            if pthinfo is not None:
                
                path,col,cellx,celly = pthinfo
                self.tv.grab_focus()
                self.tv.set_cursor( path, col, 0 )
                
                menu = self.variables[path[0]][1].create_menu( )
                menu.popup( None,None,None, event.button, event.time )

            
        
