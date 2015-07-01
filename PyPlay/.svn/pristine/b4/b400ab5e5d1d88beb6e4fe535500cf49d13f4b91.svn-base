
import math

VALUE = 0
FUNCTION = 1
ARRAY = 2

type_names = {}
type_names[ VALUE ] = "Data"
type_names[ FUNCTION ] = "Func"
type_names[ ARRAY ] = "Arry"

array_sep = '\\'

class variable (object):

    def __init__( self, name, type ):
        self.name = name
        self.type = type
        self.type_name = type_names[ self.type ]

        self.child = False
        self.has_errors = False

        self.functional = False
        self.evaluated = False

        self.sub_vars = {}
        self.dep_name = self.name
        self.dependencies = []

    @staticmethod
    def parse( name, data ):

        possible_types = [ value, function, array ]
        for poss_type in possible_types:
            
            try:
                #parse as the current type
                var = poss_type( name, data )
                
            except (ValueError, NameError, SyntaxError):
                continue

            return var
        return None

    def define( self, namespace ):
        name = self.name
        if self.child:
            name = "%s.%s" % ( self.parent_name, self.name )
        
        if not self.functional:
            namespace[ name ] = self.data
        else:
            if self.evaluate( namespace ):
                namespace[ name ] = self.eval_data

                fname = "%s.func" % self.name
                namespace[ fname ] = self.func

            else:
                print "Variable '%s' failed to evaluate." % name

        skip_children = ["eval"]
        for name,var in self.sub_vars.items():
            if not name in skip_children:
                var.define( namespace )

    def get_eval_data( self ):
        "Gets the raw data of this variable, even for functionals."
        if not self.functional:     return self.data
        elif self.evaluated:        return self.sub_vars["eval"].data
        return None
    eval_data = property( get_eval_data )

    def get_eval_var( self ):
        "Gets the variable containing evaluated variable."
        if not self.functional:     return self
        elif self.evaluated:        return self.sub_vars["eval"]
        return None
    eval_var = property( get_eval_var )

    def set_parent( self, parent, depends_on_parent ):
        self.child = True
        self.parent_name = parent.name

        if depends_on_parent:
            self.dependencies.append( parent.name )

    def get_full_name( self ):
        if self.child:
            return "%s.%s" % ( self.parent_name, self.name )
        return self.name
    full_name = property( get_full_name )

    def add_errors( self, errors ):

        errs = variable.parse( "err", errors )
        if errs is None:
            print "Failed to parse error data"
            return False

        self.has_errors = True
        self.sub_vars[ "err" ] = errs
        self.sub_vars[ "err" ].set_parent( self, depends_on_parent=False )
        return True
    
class value (variable):
    def __init__( self, name, data ):
        
        #extract floating point data, raises ValueError on problem
        super( value, self ).__init__( name, VALUE )
        
        self.data = float( data )
        self.functional = False

    def __repr__( self ):
        return str( self.data )
    
import sympy
class function (variable):

    def __init__( self, name, data ):
        
        #extract function from data, raises ValueError on problem
        super( function, self ).__init__( name, FUNCTION )
        self.functional = True
        
        try:
            split = data.split( '->' )
            variables, fn = split
            fn = fn.strip()
            
        except ValueError:
            
            #in absence of real function, create identity function
            variables = split[0]
            if len( variables.split(',') ) > 1:
                raise ValueError
            
            fn = variables.split(',')[0].strip()
            
        self.var_names = [ v.strip() for v in variables.split(',') ]
        self.dependencies.extend( self.var_names )
        
        self.vars = [ sympy.Symbol( v ) for v in self.var_names ]
        self.nvars = len( self.vars )
        
        m = [ (self.var_names[i],self.vars[i]) for i in range(self.nvars) ]
        self.var_dict = dict( m )

        self.func = eval( fn, sympy.__dict__, self.var_dict )

    def evaluate( self, namespace ):
        """Evaluate the function in the given namespace

        >>> R1 = array( "R1", array_sep.join( ['4', '2', '3'] ) )
        >>> R2 = array( "R2", array_sep.join( ['4', '12', '4'] ) )

        >>> namespace = {}
        >>> R1.define( namespace )
        >>> R2.define( namespace )
        
        >>> f = function( "f", "R1, R2 -> (R1+R2)/2" )
        >>> parsed = f.evaluate( namespace )
        >>> f.sub_vars["eval"]
        4.0, 7.0, 3.5
        """

        length = 1
        self.evaluated = False
        
        for var_name in self.var_names:
            try:
                new_length = len( namespace[ var_name ] )
                if new_length != length and length != 1:
                    raise ValueError

                if new_length != 1:
                    length = new_length
                    
            except KeyError:
                print "Undefined variable '%s', failed to evaluate." % var_name
                return False
            
            except ValueError:
                print "All variables must be same length or single-valued."
                return False
            
            except TypeError:
                #Tried to take length of single-valued variable
                pass

        built_fn = self.func
        out_data = [ 0.0 ] * length

        for i in range( length ):
            out_data[i] = self._evaluate_func( namespace, self.func, i )

        self.evaluated = True
        str_out = [ str(o) for o in out_data ]
        if length == 1:
            #create evaluated data as a raw value
            self.sub_vars[ "eval" ] = value( "eval", out_data[0] )
            
        else:
            #create evaluated data as a non-functional array
            self.sub_vars[ "eval" ] = array( "eval", array_sep.join(str_out) )

        self._analyze_error( namespace, length )
        return True

    def _analyze_error( self, namespace, length ):

        self.orig_func = self.func
        self.err_funcs = [ sympy.diff( self.func, v ) for v in self.vars ]
        print self.err_funcs

        found_error = False
        for var in self.vars:
            
            if ("%s.err" % var.name) in namespace.keys():
                found_error = True
                break

        if not found_error:
            return

        out_err = [0.0] * length
        for i in range( length ):

            err_accum = 0.0
            for e,var in enumerate( self.vars ):
                
                if ("%s.err"%var.name) in namespace.keys():
                    try:
                        err = namespace[ "%s.err" % var.name ][i].data
                    except TypeError:
                        err = namespace[ "%s.err" % var.name ]
                        
                    diff = self._evaluate_func( namespace, self.err_funcs[e], i )
                    err_accum += (diff * err)**2
                
            out_err[i] = math.sqrt( err_accum )

        str_out = [ str(o) for o in out_err ]
        if length == 1:
            #create evaluated data as a raw value
            self.sub_vars[ "err" ] = value( "err", out_err[0] )
            
        else:
            #create evaluated data as a non-functional array
            self.sub_vars[ "err" ] = array( "err", array_sep.join(str_out) )

        self.sub_vars[ "err" ].set_parent( self, depends_on_parent=True )
        print "CalcErrs", repr( self.sub_vars["err"] )
        
    def _evaluate_func( self, namespace, func, i ):

        for var in self.vars:
            try:
                definition = namespace[var.name][i].data
                    
            except TypeError:
                # This variable is single valued
                definition = namespace[var.name]
                    
            func = func.subs( var, definition )
        return func.evalf()
                

    def __repr__( self ):
        return "%s -> %s" % ( ', '.join( self.var_names ), repr( self.func ) )

class array (variable):

    def __init__( self, name, data ):

        super( array, self ).__init__( name, ARRAY )
        self.functional = False
        
        self.data = []
        arr = data.split( array_sep )
        
        for i, val in enumerate( arr ):

            try:
                elem_name = "%s_%d" % (name, i)
                self.data.append( value( elem_name, val ) )
                
            except ValueError:
                self.functional = True
                self.data.append( function( elem_name, val ) )

    def evaluate( self, namespace ):
        
        self.evaluated = False
        raw_data = []
        
        for d in self.data:
            
            if d.type == FUNCTION:

                if (not d.evaluate( namespace ) or
                    d.sub_vars["eval"].type != VALUE):
                    
                    return False
                raw_data.append( d.sub_vars["eval"].data )

            else:
                raw_data.append( d.data )

        self.evaluated = True
        self.sub_vars[ "eval" ] = array( "eval", array_sep.join( raw_data ) )  
        return True

    def calc_stats( self ):

        if self.functional and not self.evaluated:
            print "Cannot calculate stats, not evaluated."
            return

        if self.functional:     data = self.sub_vars["eval"].data
        else:                   data = self.data

        mean = sum( [x.data for x in data] ) / float( len(data) )
        std_dev_sum = sum( [(x.data-mean)**2 for x in data] )
        std_dev = math.sqrt( std_dev_sum / float( len(data)-1 ) )

        self.sub_vars["mean"] = value( "mean", mean )
        self.sub_vars["mean"].set_parent( self, depends_on_parent = True )
        
        self.sub_vars["sdev"] = value( "sdev", std_dev )
        self.sub_vars["sdev"].set_parent( self, depends_on_parent = True )
        
    def __repr__( self ):
        return ', '.join( [ str(d) for d in self.data ] )

import pygtk
pygtk.require('2.0')
import gtk

from util_window import *
class variable_viewer:

    def __init__( self, store, depgraph, var, parent = None ):
        
        self.parent = parent
        self.var = var
        self.name = self.var.full_name

        self.sub_views = {}
        
        self.store = store
        self.dep_graph = depgraph
        

        if var.functional:
            if var.evaluated:   data_out = repr( var.sub_vars["eval"] )
            else:               data_out = "Not evaluated."

            #add the function below the calculated data
            self.iter = self.store.append( self.parent, ["", "", ""] )
            self.func_iter = self.store.append( self.iter, ["", "", ""] )
            self.set_store_data = self.set_store_data_func

        else:
            self.iter = self.store.append( self.parent, ["", "", ""] )
            self.set_store_data = self.set_store_data_nonfunc

        #Call set store once in case dep_graph doesn't evaluate it
        self.set_store_data()
        self.dep_graph.insert( self, self.var.dependencies, self.update )

    def set_store_data_func( self ):
        if self.var.evaluated:  data_out = self.var.eval_var
        else:                   data_out = "Not evaluated."
        
        self.store.set( self.iter, 0, self.var.name, 1, self.var.type_name,
                        2, repr(data_out) )

        self.store.set( self.func_iter, 0, "func", 1, self.var.type_name,
                        2, repr(self.var) )
        self.set_store_subvars()
        
    def set_store_data_nonfunc( self ):
        self.store.set( self.iter, 0, self.var.name, 1, self.var.type_name,
                        2, repr(self.var) )
        self.set_store_subvars()

    def set_store_subvars( self ):

        self.update_subvars()
        for name, sview in self.sub_views.items():

            #check for sview being None here because of our hack
            #in update_subvars
            
            if sview is not None:
                sview.set_store_data()

    def update( self, namespace ):
        self.var.define( namespace )
        self.set_store_data()

    def update_subvars( self ):

        skipped = ["eval"]

        #update and add any new subvariables we're not displaying
        for name, var in self.var.sub_vars.items():
            if name not in self.sub_views.keys() and name not in skipped:

                #have to add something to sub_views before creating new
                #variable viewer, otherwise we get an infinite loop
                #if dep_graph rebuilds us
                
                self.sub_views[name] = None
                self.sub_views[name] = variable_viewer( self.store,
                                self.dep_graph, var, self.iter )
        
    def calc_stats( self ):
        self.var.calc_stats()
        self.update_subvars()        

    def add_errors( self, err ):
        self.var.add_errors( err )
        self.update_subvars()

    def create_add_errors( self ):
        create_error_dialog( None, self )
        
    def create_menu( self ):

        self.menu_fns = {
        "calc_stats": lambda widget, var: self.calc_stats(),
        "add_errors": lambda widget, var: self.create_add_errors()
        }
        
        self.menu_items = (
        ( "/Add _Stats", "<control>S", self.menu_fns["calc_stats"], 0, None ),
        ( "/Add _Errors", "<control>E", self.menu_fns["add_errors"], 0, None ),
        )

        accel_group = gtk.AccelGroup()
        self.item_factory = gtk.ItemFactory( gtk.Menu, "<main>", accel_group )
        self.item_factory.create_items( self.menu_items )
        return self.item_factory.get_widget( "<main>" )


if __name__ == "__main__":
    import doctest
    doctest.testmod()
