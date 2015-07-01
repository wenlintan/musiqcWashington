
import pygame
from pygame.locals import *

import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.shaders import * 
from OpenGL.GL.framebufferobjects import *
#from OpenGL.arrays import ArrayDatatype as ADT

from itertools import *
from ctypes import *
import pdb

import numpy
from numpy import sin, cos, sqrt

class Renderer:
    def __init__( self, width, height ):
        self.width, self.height = width, height
        
        pygame.init()
        flags =  pygame.OPENGL | pygame.DOUBLEBUF
        screen = pygame.display.set_mode( (width, height), flags, 32 )

        print glGetString( GL_VERSION )

        glClearColor( 0.0, 0.0, 0.0, 1.0 )
        glClearDepth( 1.0 )
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

        glEnable( GL_DEPTH_TEST )
        glEnable( GL_CULL_FACE )

        glViewport( 0, 0, width, height )

        self.ortho()
        self.origin()
        pygame.display.flip()

    def __del__( self ):
        pygame.quit()

    def begin_frame( self ):
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

    def end_frame( self ):
        pygame.display.flip()

    def reset_target( self ):
        glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, 0 )
        glViewport( 0, 0, self.width, self.height )
        
    def origin( self ):
        """Set modelview matrix to identity."""
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()

    def world( self, pos, look, up ):
        """Set modelview matrix to current camera orientation."""
        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()

        gluLookAt(
                pos[0], pos[1], pos[2],
                look[0] + pos[0], look[1] + pos[1], look[2] + pos[2],
                up[0], up[1], up[2],
            )

    def perspective( self, fov, nearz, farz ):
        """Setup projection matrix using internal parameters."""
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        aspect = float(self.width) / self.height
        gluPerspective( fov, aspect, nearz, farz )

    def ortho( self ):
        """Setup projection matrix for orthographic projection."""
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        glOrtho( 0.0, self.width, 0.0, self.height, -1.0, 1.0 )
		
class Camera:
    def __init__( self, position, look, up ):
        self.position = numpy.array(position)
        self.look = numpy.array(look)
        self.up = numpy.array(up)

        self.rotation = numpy.array((0., 0.))
        self.translation = numpy.array((0., 0.))

    @staticmethod
    def _cross_product_matrix( x ):
         return numpy.array((
             (0., -x[2], x[1]), 
             (x[2], 0., -x[0]), 
             (-x[1], x[0], 0.)
         ))

    def rotate( self, x, y ):
        sx, cx = sin(x), cos(x)
        sy, cy = sin(y), cos(y)

        right = numpy.cross( self.look, numpy.array((0., 1., 0.)) )
        right = right / numpy.linalg.norm( right )

        rotx = (
            cx * numpy.identity( 3 ) +
            sx * self._cross_product_matrix( right ) +
            (1. - cx) * numpy.outer( right, right )
        )
        roty = numpy.array(((cy, 0., sy), (0., 1., 0.), (-sy, 0., cy)))

        self.look = numpy.dot( rotx, numpy.dot( roty, self.look ) )
        if self.look[1] > 0.9 or self.look[1] < -0.9:
            scale = sqrt(.19 / (self.look[0]**2 + self.look[2]**2))
            y = 0.9 if self.look[1] > 0.9 else -0.9
            self.look = numpy.array((scale*self.look[0], y, scale*self.look[2]))
        self.look = self.look / numpy.linalg.norm(self.look)
    
        right = numpy.cross( self.look, numpy.array((0., 1., 0.)) )
        self.up = numpy.cross( right, self.look ) 
        self.up = self.up / numpy.linalg.norm(self.up)
    
    def translate( self, dx, dz ):
        right = numpy.cross( self.look, numpy.array((0., 1., 0.)) )
        self.position += right*dx + self.look*dz
	
    def set_translation( self, x = None, z = None ):
        if x is not None: self.translation[0] = x
        if z is not None: self.translation[1] = z
	
    def set_rotation( self, x = None, y = None ):
        if x is not None: self.rotation[0] = x
        if y is not None: self.rotation[1] = y

    def update( self, renderer ):
        self.rotate( self.rotation[0], self.rotation[1] )
        self.translate( self.translation[0], self.translation[1] )
        renderer.world( self.position, self.look, self.up )

class Texture:
    glTexImageFn = { 1: glTexImage1D, 2: glTexImage2D, 3: glTexImage3D }
    glTarget = { 1: GL_TEXTURE_1D, 2: GL_TEXTURE_2D, 3: GL_TEXTURE_3D }

    def __init__( self, data, data_dimensions,
                data_type = GL_UNSIGNED_BYTE, 
                data_format = GL_RGB, 
                gl_precision = GL_RGB,
                min_filter = GL_LINEAR, 
                mag_filter = GL_LINEAR, 
                wrap_s = GL_REPEAT,
                wrap_t = GL_REPEAT
            ):
        
        ndimensions = len( data_dimensions )
        self.target = self.glTarget[ ndimensions ]

        self.texture = glGenTextures( 1 )
        glBindTexture( self.target, self.texture )

        glTexParameter( self.target, GL_TEXTURE_MIN_FILTER, min_filter )
        glTexParameter( self.target, GL_TEXTURE_MAG_FILTER, mag_filter )
        glTexParameter( self.target, GL_TEXTURE_WRAP_S, wrap_s )
        glTexParameter( self.target, GL_TEXTURE_WRAP_T, wrap_t )
        
        args = [ self.target, 0, gl_precision, ]
        args.extend( data_dimensions )
        args.extend( [0, data_format, data_type, data] )
        #print args
        self.glTexImageFn[ ndimensions ] ( *args )
        print "Loaded."

    def apply( self, active_texture = 0 ):
        glEnable( self.target )
        glActiveTexture( GL_TEXTURE0 + active_texture )
        glBindTexture( self.target, self.texture )

    def __del__( self ):
        glDeleteTextures( self.texture )

class Color:
    def __init__( self, *data ):
        self.r, self.g, self.b = data

class Material:
    cache = {}

    @staticmethod
    def load( filename ):
        if filename not in Material.cache:
            image = pygame.image.load( filename )
            data = pygame.image.tostring( image, "RGB", 1 )
            width, height = image.get_width(), image.get_height()
            print width, height
            Material.cache[ filename ] = Material( data, (width, height), filename )
        return Material.cache[ filename ]

    def __init__( self, data, dims, filename = None, 
	              precision = GL_RGB, format = GL_RGB, type = GL_UNSIGNED_BYTE,
                  filter = GL_LINEAR
            ):
        self.filename = filename
        self.texture = Texture( data, dims, type, format, precision, filter, filter )

    def apply( self, active_texture = 0 ):
        self.texture.apply(active_texture)

class FBO:
    DEPTH = 0
    STENCIL = 0
    
    glFramebufferTextureFn = {
            GL_TEXTURE_2D: glFramebufferTexture2D,
            GL_TEXTURE_3D: glFramebufferTexture3D
        }
    
    def __init__( self, dimensions, textures = [], layers = [] ):
        self.fbo = glGenFramebuffers( 1 )
        self.width, self.height = dimensions
        self.textures = textures
        self.apply()

        for i, tex in enumerate( textures ):
            index = GL_COLOR_ATTACHMENT0_EXT + i
            if layers and layers[ i ] != -1:
                fn = glFramebufferTextureLayer
                fn( GL_FRAMEBUFFER_EXT, index, tex.texture.texture, 0, layers[i] )
            else:
                fn = self.glFramebufferTextureFn[ tex.target ]
                fn( GL_FRAMEBUFFER_EXT, index, tex.target, tex.texture, 0 )
		glDrawBuffers( [GL_COLOR_ATTACHMENT0_EXT + i for i in range( len( textures ) )] )

    def attach( self, type ):
        self.zbuffering = True
        
        self.depth_tex = glGenRenderbuffers( 1 )
        glBindRenderbufferEXT( GL_RENDERBUFFER_EXT, self.depth_tex )
        glRenderbufferStorageEXT( GL_RENDERBUFFER_EXT, 
            GL_DEPTH_COMPONENT, self.width, self.height )

        glBindFramebuffer( GL_FRAMEBUFFER_EXT, self.fbo )
        glFramebufferRenderbufferEXT( GL_FRAMEBUFFER_EXT, 
            GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT,
            self.depth_tex )

    def apply( self ):
        glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, self.fbo )
        glViewport( 0, 0, self.width, self.height )
        glDrawBuffers( [GL_COLOR_ATTACHMENT0_EXT + i for i in range( len( self.textures ) )] )

    def perspective( self, fov, nearz, farz ):
        """Setup projection matrix using internal parameters."""
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        aspect = float(self.width) / self.height
        gluPerspective( fov, aspect, nearz, farz )

    def ortho( self ):
        """Setup projection matrix for orthographic projection."""
        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        glOrtho( 0.0, self.width, 0.0, self.height, -1.0, 1.0 )

    def __del__( self ):
        if( glDeleteFramebuffersEXT ):
            glDeleteFramebuffersEXT( self.fbo )

class Program:
    cache = {}
    geom_separator = "--Geometry/Fragmet--"
    frag_separator = "--Vertex/Fragment--"

    class VertexAttrib:
        pass
    Vertex = VertexAttrib()
    Normal = VertexAttrib()
    Color = VertexAttrib()
    TexCoord0 = VertexAttrib()
    
    class VariableHelper:
        def __init__( self, prog ):
            self.program = prog
        
        def __setattr__( self, name, value ):
            if name == "program":
                self.__dict__[ name ] = value
                return
            try:
                self.program.set( name, *value )
            except:
                self.program.set( name, value )

    @staticmethod
    def load( filename, frag_loc ):
        with file( filename ) as f:
            return Program.create( '\n'.join( f.readlines() ), frag_loc )

    @staticmethod
    def create( data, *frag_loc ):
        if data not in Program.cache:
            Program.cache[ data ] = Program( data, *frag_loc )

        return Program.cache[ data ]

    def __init__( self, code, *frag_outs ):
        self.code = code
        self.attrib_pointer = {}

        ( self.vertex_code, _, self.fragment_code
            ) = code.partition( self.frag_separator )

        self.program = glCreateProgram()
        ( self.geometry_code, _, self.vertex_code
            ) = self.vertex_code.partition( self.geom_separator )

        self.codes = {}
        self.codes[ GL_FRAGMENT_SHADER ] = self.fragment_code
        if self.vertex_code:
            self.codes[ GL_GEOMETRY_SHADER ] = self.geometry_code
        else:
            self.vertex_code = self.geometry_code
        self.codes[ GL_VERTEX_SHADER ] = self.vertex_code

        self.shaders = {}
        for type, src in self.codes.items():
            self.shaders[ type ] = glCreateShader( type )
            glShaderSource( self.shaders[ type ], src )
            glCompileShader( self.shaders[ type ] )
            glAttachShader( self.program, self.shaders[ type ] )

        glLinkProgram( self.program )
        if not glGetProgramiv( self.program, GL_LINK_STATUS ):
            print glGetProgramInfoLog( self.program )
            raise ValueError( "Program did not link." )
        glUseProgram( self.program )

        for i, out in enumerate( frag_outs ):
            glBindFragDataLocation( self.program, i, out )
        
        self._set_functions = {}
        self._capture_variables()
        self.variables = Program.VariableHelper( self )

    def set_matrices_from_gl( self, modelview_name, proj_name ):
        modelview = glGetFloatv( GL_MODELVIEW_MATRIX )
        projection = glGetFloatv( GL_PROJECTION_MATRIX )
        self.set( modelview_name, modelview )
        self.set( proj_name, projection )

    set_attrib = {
        GL_FLOAT: glVertexAttrib1f,
        GL_FLOAT_VEC2: glVertexAttrib2f,
        GL_FLOAT_VEC3: glVertexAttrib3f,
        GL_FLOAT_VEC4: glVertexAttrib4f
    }

    set_attrib_ptr = {
        GL_FLOAT_VEC2: ( 2, GL_FLOAT ),
        GL_FLOAT_VEC3: ( 3, GL_FLOAT ),
        GL_FLOAT_VEC4: ( 4, GL_FLOAT )
    }

    set_uniform = {
        GL_INT: ( glUniform1i, glUniform1iv ),
        GL_FLOAT: ( glUniform1f, glUniform1fv ),
        GL_FLOAT_VEC3: ( glUniform3f, glUniform3fv ),
        GL_FLOAT_VEC4: ( glUniform4f, glUniform4fv ),
        GL_FLOAT_MAT4: glUniformMatrix4fv,
        GL_SAMPLER_1D: ( glUniform1i, ),
        GL_SAMPLER_2D: ( glUniform1i, ),
        GL_SAMPLER_3D: ( glUniform1i, ),
        GL_INT_SAMPLER_1D: ( glUniform1i, ),
        GL_INT_SAMPLER_2D: ( glUniform1i, ),
        GL_INT_SAMPLER_3D: ( glUniform1i, )
    }
    
    def set( self, name, *data ):
        self.apply()
        self._set_functions[ name ]( data )
        
    def _capture_uniform( self, index ):
        name, size, data_type = glGetActiveUniform( self.program, index )
        loc = glGetUniformLocation( self.program, name )
        print "Uniform:", name, size, data_type, loc, GL_SAMPLER_3D
        
        if data_type in ( GL_FLOAT_MAT4, ):
            f = lambda d: self.set_uniform[ data_type ]( loc, size, False, d[0] )
        elif size == 1:
            f = lambda d: self.set_uniform[ data_type ][ 0 ]( loc, *d )
        else:
            f = lambda d: self.set_uniform[ data_type ][ 1 ]( loc, size, d[0] )
        self._set_functions[ name ] = f
        
    def _capture_attrib( self, index ):
        length, name = GLsizei(0), c_char_p('\0'*100)
        data_type, size = GLuint(0), GLint(0)
        glGetActiveAttrib( self.program, index, 100, pointer(length), 
                pointer(size), pointer(data_type), name )

        size, data_type, name = size.value, data_type.value, name.value
        loc = glGetAttribLocation( self.program, name )
        print "Attrib:", name, size, data_type, loc

        def set_attrib_fn( data, data_type=data_type ):
            print "set", data[0]
            if isinstance( data[0], self.VertexAttrib ):
                #Will bind actual data later using glVertexAttribPointer
                print "Bind temp."
                size, data_type = self.set_attrib_ptr[ data_type ]
                self.attrib_pointer[ data[0] ] = ( loc, size, data_type ) 
            else:
                #Otherwise assume we're just assigning one value
                self.set_attrib[ data_type ]( loc, *data )
        self._set_functions[ name ] = set_attrib_fn
        
    def _capture_variables( self ):
        nuniforms = glGetProgramiv( self.program, GL_ACTIVE_UNIFORMS )
        nattribs = glGetProgramiv( self.program, GL_ACTIVE_ATTRIBUTES )

        for u in range( nuniforms ):
            self._capture_uniform( u )

        for a in range( nattribs ):
            self._capture_attrib( a )

    def bind( self, data_type, raw_type, data ):
        loc, size, data_type = self.attrib_pointer[ data_type ]
        norm = False if raw_type == GL_FLOAT else True
        glVertexAttribPointer( loc, size, raw_type, norm, 0, data )
        glEnableVertexAttribArray( loc )
    
    def apply( self ):
        glUseProgram( self.program )

    def __del__( self ):
        if( bool(glDeleteProgram) ):
            glDeleteProgram( self.program )

class Batch:
    Vertex = 0
    Normal = 1
    Color = 2
    TexCoord0 = 3
    Index = 100
    
    F2 = 0
    F3 = 1
    UB4 = 2
    US1 = 3
    
    type_data = {
            F2: (GL_FLOAT, GLfloat, 2),
            F3: (GL_FLOAT, GLfloat, 3),
            UB4: (GL_UNSIGNED_BYTE, GLubyte, 4),
            US1: (GL_UNSIGNED_SHORT, GLushort, 1)
        }
    
    data_function = {
            Vertex: ("vertices", GL_VERTEX_ARRAY, glVertexPointer, Program.Vertex),
            Normal: ("normals", GL_NORMAL_ARRAY, glNormalPointer, Program.Normal),
            Color: ("colors", GL_COLOR_ARRAY, glColorPointer, Program.Color),
            TexCoord0: (
                "texcoord0", GL_TEXTURE_COORD_ARRAY,
                lambda s, t, st, p: 
                    (glClientActiveTexure(GL_TEXTURE0), glTexCoordPointer(s,t,st,p)),
                Program.TexCoord0
            ),

            Index: ("indices", GL_INDEX_ARRAY, None, None)
        }

    class DrawData:
        BOUNDED = 0
        INSTANCED = 1

        @staticmethod
        def bounded( start, stop ):
             return Batch.DrawData(data_type = Batch.DrawData.BOUNDED, bounds = (start,stop))

        @staticmethod
        def instanced( n ):
             return Batch.DrawData(data_type = Batch.DrawData.INSTANCED, n = n)

        def __init__( self, **keys ):
            self.__dict__.update( keys )

    def __init__( self, draws ):
        self.draws = draws
        if not len( draws ):
            raise AttributeError( "Must have something." )

        if not glGenBuffers:
            raise AttributeError( "No VBOs." )
        
        self.vertex_buffer = None
        self.rebuild( True )

    def rebuild( self, recreate = False ):
        nv, ni = 0, 0
        for d in self.draws:
            d.set_offsets( nv, ni )
            nv, ni = nv + d.nvertices, ni + d.nindices
        self.nvertices, self.nindices = nv, ni

        built_data = {}
        cls = self.draws[0].__class__
        dtypes = cls.batch_data
        for data, dtype in dtypes.iteritems():
            name, gl_state, gl_set, prog_set = self.data_function[ data ]
            fn = getattr( cls, name )
            built_data[data] = self._generate_data( dtype, fn, self.draws, data == self.Index )

        if self.Index in built_data:
            self.indices = built_data.pop( self.Index )
            self.index_gl_type = self.type_data[dtypes[ self.Index ]][0]
            self.draw = self._draw_indexed
        else:
            self.draw = self._draw

        self.buffers, self.data_types = {}, {}
        for data, bdata in built_data.items():
            self.buffers[ data ] = glGenBuffers(1)
            self.data_types[ data ] = dtypes[ data ]
            glBindBuffer( GL_ARRAY_BUFFER_ARB, self.buffers[data] )
            glBufferData( GL_ARRAY_BUFFER_ARB, sizeof(bdata), bdata, GL_DYNAMIC_DRAW )

    def _draw( self, draw_data = None, shader = None ):
        self._bind( shader )
        if draw_data is not None and draw_data.data_type == self.DrawData.INSTANCED:
            glDrawArraysInstanced( GL_TRIANGLES, 0, self.nvertices, draw_data.n )
            return

        start, stop = 0, self.nvertices
        if draw_data is not None and draw_data.data_type == self.DrawData.BOUNDED:
            start, stop = draw_data.bounds
        glDrawArrays( GL_TRIANGLES, start, stop )

    def _draw_indexed( self, draw_data = None, shader = None ):
        self._bind( shader )
        start, stop = 0, self.nindices
        if draw_data is not None and draw_data.data_type == self.DrawData.BOUNDED:
            start, stop = draw_data.bounds

        glDrawElements( GL_TRIANGLES, stop-start,
                self.index_gl_type, byref(self.indices, start) )
    
    def _bind( self, shader ):
        bind = self._bind_data
        if shader is not None:
            bind = self._bind_data_program
        
        for data, dtype in self.data_types.items():
            bind( self.buffers[data], data, dtype, shader )

    def _bind_data_program( self, buffer, data, data_type, program ):
        name, gl_state, gl_set, prog_set = self.data_function[ data ]
        gl_type, c_type, n = self.type_data[ data_type ]
        
        glDisableClientState( gl_state )
        glBindBuffer( GL_ARRAY_BUFFER_ARB, buffer )
        program.bind( prog_set, gl_type, None )
    
    def _bind_data( self, buffer, data, data_type, program = None ):
        name, gl_state, gl_set, prog_set = self.data_function[ data ]
        gl_type, c_type, n = self.type_data[ data_type ]
        
        glBindBuffer( GL_ARRAY_BUFFER_ARB, buffer )
        gl_set( n, gl_type, 0, None )
        glEnableClientState( gl_state )

    def _generate_data( self, data_type, fn, draws, index = False ):
        nitems = self.nvertices
        if index:
            nitems = self.nindices
        
        gl_type, c_type, n = self.type_data[ data_type ]
        iterator = chain.from_iterable( fn(d) for d in draws )
        if n > 1:
            iterator = chain.from_iterable( iterator )
        
        arr_type = c_type * (nitems * n)
        return arr_type( *iterator )

