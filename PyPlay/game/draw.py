
from OpenGL.GL import *

from vector import *
import renderer

class nothing:
    def apply( self ):
        pass

    def __lt__( self, o ):
        if isinstance( o, nothing ):
            return False
        return True

class state:
    def __init__( self ):
        self.material = nothing()
        self.vertex_shader = nothing()
        self.fragment_shader = nothing()

    def set_mat( self, mat ):
        self.material = mat
        return self

    def set_vs( self, vs ):
        self.vertex_shader = vs
        return self

    def set_fs( self, fs ):
        self.fragment_shader = fs
        return self

    def apply( self ):
        self.material.apply()
        self.vertex_shader.apply()
        self.fragment_shader.apply()

    def __lt__( self, o ):
        if self.material < o.material:
            return True
        if o.material < self.material:
            return False
        
        if self.vertex_shader < o.vertex_shader:
            return True
        if o.vertex_shader < self.vertex_shader:
            return False
        
        if self.fragment_shader < o.fragment_shader:
            return True
        if o.fragment_shader < self.fragment_shader:
            return False
        return False

    def __eq__( self, o ):
        return NotImplemented

class draw:
    def __init__( self ):
        self.state = state()

    def register( self, renderer ):
        self.renderer = renderer

    def draw( self ):
        "Draw will be called to render this item after self.state has been applied."
        
        print "ERROR: draw::draw must be overrided"
        raise AttributeError

class triangle ( draw ):
    def __init__( self, p0, p1, p2, t0 = None, t1 = None, t2 = None ):
        draw.__init__( self )
        
        self.points = [ p0, p1, p2 ]
        self.tex = [ t0, t1, t2 ]

    def draw( self ):

        if not glIsEnabled( GL_TEXTURE_2D ):
            glBegin( GL_TRIANGLES )
            glVertex3f( self.points[0].x, self.points[0].y, self.points[0].z )
            glVertex3f( self.points[1].x, self.points[1].y, self.points[1].z )
            glVertex3f( self.points[2].x, self.points[2].y, self.points[2].z )
            glEnd()
        else:
            glBegin( GL_TRIANGLES )
            glTexCoord2f( self.tex[0].x, self.tex[0].y )
            glVertex3f( self.points[0].x, self.points[0].y, self.points[0].z )
            glTexCoord2f( self.tex[1].x, self.tex[1].y )
            glVertex3f( self.points[1].x, self.points[1].y, self.points[1].z )
            glTexCoord2f( self.tex[2].x, self.tex[2].y )
            glVertex3f( self.points[2].x, self.points[2].y, self.points[2].z )
            glEnd()

class mesh ( draw ):
    def __init__( self, vertices ):
        draw.__init__( self )

        self.verts = vertices
        self.l = len( self.verts )

    def set_vertices( self, verts ):
        self.verts = verts

    def draw( self ):

        glBegin( GL_LINES )
        for i in range( -1, self.l-1 ):
            glVertex3f( self.verts[i].x, self.verts[i].y, self.verts[i].z )
            glVertex3f( self.verts[i+1].x, self.verts[i+1].y, self.verts[i+1].z )
        glEnd()

class filled_mesh( draw ):
    def __init__( self, vertices ):
        draw.__init__( self )
        
        self.verts = vertices
        self.l = len( self.verts )

    def set_vertices( self, verts ):
        self.verts = verts

    def draw( self ):
        pass

        
