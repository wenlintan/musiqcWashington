
import copy
class edge:
    def __init__( self, one, two ):
        self.s = one
        self.e = two

    def reverse( self ):
        return edge( self.e, self.s )

class graph:

    def __init__( self ):
        
        self.all_nodes = []
        self.nodes = {}
        
        self.dep_edges = {}
        self.temp_dep_edges = {}
        self.edges = {}

        self.namespace = {}

    def insert( self, node, depends, update_fn ):

        node.dep_update_fn = update_fn
        self.all_nodes.append( node )
        self.nodes[ node.name ] = node

        new_edges = [ edge(node.name, d) for d in depends ]
        self.dep_edges[ node ] = new_edges

        #must rebuild edges of correct direction from dependency edges
        self.build_edges()
        self.build_topological_order()
        self.evaluate()

    def build_edges( self ):

        for node in self.all_nodes:
            self.edges[ node ] = []

        for node in self.all_nodes:
            for dep_e in self.dep_edges[ node ]:

                try:
                    self.edges[ self.nodes[dep_e.e] ].append( dep_e.reverse() )
                except KeyError:
                    print "Dependency '%s' not found" % dep_e.e

    def build_topological_order( self ):

        no_incoming = []
        self.topo_order = []
        
        for node in self.all_nodes:
            if not len( self.dep_edges[ node ] ):
                no_incoming.append( node )
            self.temp_dep_edges[ node ] = copy.copy( self.dep_edges[node] )

        while len(no_incoming):
            node = no_incoming.pop()
            self.topo_order.append( node )

            for edge in self.edges[node]:
                
                other = self.nodes[ edge.e ]
                for i, dep_edge in enumerate( self.temp_dep_edges[ other ] ):
                    if dep_edge.e == node.name:
                        delete = i

                del self.temp_dep_edges[other][delete]
                if not len( self.temp_dep_edges[other] ):
                    no_incoming.append( other )

                

        if len( self.topo_order ) != len( self.all_nodes ):
            print "Cyclic dependency! Explosion imminent!"

    def evaluate( self ):

        self.namespace = {}
        for node in self.topo_order:
            node.dep_update_fn( self.namespace )

        
            

                
        

                
                

        

        
        
