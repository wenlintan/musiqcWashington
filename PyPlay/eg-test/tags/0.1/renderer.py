
import pygame
from pygame.locals import *

import OpenGL
from OpenGL.GL import *
from OpenGL.GL.shaders import * 
from OpenGL.arrays import ArrayDatatype as ADT

from itertools import *
from ctypes import *
import numpy


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

        glMatrixMode( GL_PROJECTION )
        glLoadIdentity()
        glOrtho( 0, width, 0, height, -1, 1 )

        glMatrixMode( GL_MODELVIEW )
        glLoadIdentity()

        pygame.display.flip()

    def __del__( self ):
        pygame.quit()

    def begin_frame( self ):
        glClear( GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT )

    def end_frame( self ):
        pygame.display.flip()

class Tile:
    width, height = 32, 32
    offsets = ( (0,0), (width, 0), (0, height), (width, height) )
    index_data = ( 0, 1, 2, 1, 3, 2 )
    
    def __init__( self, x, y, color = None ):
        self.x, self.y = x * 32, y * 32
        self.color = color
        
        if color is None:
            cmap = lambda v: min( int(v * 255), 255 )
            self.color = cmap(self.x), cmap(self.y), 0, 255
        
        self.dirty = False

    def set_offsets( self, vertex_off, index_off ):
        self.vertex_offset, self.index_offset = vertex_off, index_off

    nvertices = 4
    def vertices( self ):
        return ((self.x + x, self.y + y, 0.5) for x, y in self.offsets)

    def colors( self ):
        return (self.color for _ in range(self.nvertices))

    nindices = 6
    def indices( self ):
        return (i + self.vertex_offset for i in self.index_data)

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
        self.target = glTarget[ ndimensions ]

        self.texture = glGenTexture( 1 )
        glBindTexture( self.target, self.texture )

        glTexParameter( self.target, GL_TEXTURE_MIN_FILTER, min_filter )
        glTexParameter( self.target, GL_TEXTURE_MAG_FILTER, mag_filter )
        glTexParameter( self.target, GL_TEXTURE_WRAP_S, wrap_s )
        glTexParameter( self.target, GL_TEXTURE_WRAP_T, wrap_t )

        args = [ self.target, 0, gl_precision ]
        args.extend( data_dimensions )
        args.extend( ( 0, data_format, data_type, data ) )
        glTexImageFn[ ndimensions ] ( *args )

    def apply( self ):
        glEnable( GL_TEXTURE_2D )
        glBindTexture( GL_TEXTURE_2D, self.texture )

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
            Material.cache[ filename ] = Material( filename )

        return Material.cache[ filename ]
    
    def __init__( self, filename ):
        self.filename = filename
        
        image = pygame.image.load( filename )
        data = pygame.image.tostring( image, "RGB", 1 )
        self.width, self.height = image.get_width(), image.get_height()

        self.texture = Texture( data, ( self.width, self.height ) )

    def apply( self ):
        self.texture.apply()

class FBO:
    def __init__( self, dimensions, textures = [], zbuffering = False ):
        self.fbo = glGenFramebuffers( 1 )
        self.width, self.height = dimensions
        glBindFramebuffer( GL_FRAMEBUFFER_EXT, self.fbo )

        self.textures = textures
        for i, tex in enumerate( textures ):
            index = GL_COLOR_ATTACHMENT0_EXT + i
            glFramebufferTexture2D( GL_FRAMEBUFFER_EXT, index, 
                    tex.target, tex.texture, 0 )

        self.zbuffering = zbuffering
        if zbuffering:
            self.depth_tex = glGenRenderbuffers( 1 )
            glBindRenderbufferEXT( GL_RENDERBUFFER_EXT, self.depth_tex )
            glRenderbufferStorageEXT( GL_RENDERBUFFER_EXT, 
                    GL_DEPTH_COMPONENT, self.width, self.height )

            glFramebufferRenderbufferEXT( GL_FRAMEBUFFER_EXT, 
                    GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT,
                    self.depth_tex )

        glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, 0 )

    def apply( self ):
        glBindFramebufferEXT( GL_FRAMEBUFFER_EXT, self.fbo )
        glViewport( 0, 0, self.width, self.height )

    def __del__( self ):
        glDeleteFramebuffers( self.fbo )

class Program:
    cache = {}
    seperator = "--Vertex/Fragment--"

    class VertexAttrib:
        pass
    Vertex = VertexAttrib()
    Normal = VertexAttrib()
    Color = VertexAttrib()
    TexCoord0 = VertexAttrib()

    @staticmethod
    def load( filename, frag_loc ):
        with file( filename ) as f:
            return Program.create( '\n'.join( f.readlines() ), frag_loc )

    @staticmethod
    def create( data, frag_loc ):
        if data not in Program.cache:
            Program.cache[ data ] = Program( data, frag_loc )

        return Program.cache[ data ]

    def __init__( self, code, frag_out ):
        self.code = code
        self.attrib_pointer = {}

        ( self.vertex_code, _, self.fragment_code
                ) = code.partition( self.seperator )

        self.program = compileProgram(
                compileShader( self.vertex_code, GL_VERTEX_SHADER ),
                compileShader( self.fragment_code, GL_FRAGMENT_SHADER )
                )

        glBindFragDataLocation( self.program, 0, frag_out ) 
        self._capture_variables()

    def set_matrices_from_gl( self, modelview_name, proj_name ):
        modelview = glGetFloatv( GL_MODELVIEW_MATRIX )
        projection = glGetFloatv( GL_PROJECTION_MATRIX )
        self.set_variable( modelview_name, modelview )
        self.set_variable( proj_name, projection )
    
    def set_variable( self, name, data ):
        setattr( self.vars, name, data )

    set_attrib = {
        GL_FLOAT: glVertexAttrib1f,
        GL_FLOAT_VEC3: glVertexAttrib3f,
        GL_FLOAT_VEC4: glVertexAttrib4f
    }

    set_attrib_ptr = {
        GL_FLOAT_VEC3: ( 3, GL_FLOAT ),
        GL_FLOAT_VEC4: ( 4, GL_FLOAT )
    }

    set_uniform = {
        GL_INT: ( glUniform1i, glUniform1iv ),
        GL_FLOAT: ( glUniform1f, glUniform1fv ),
        GL_FLOAT_VEC3: ( glUniform3f, glUniform3fv ),
        GL_FLOAT_VEC4: ( glUniform4f, glUniform4fv ),
        GL_FLOAT_MAT4: glUniformMatrix4fv
    }

    def _capture_variables( self ):
        print "Getting data."
        nuniforms = glGetProgramiv( self.program, GL_ACTIVE_UNIFORMS )
        nattribs = glGetProgramiv( self.program, GL_ACTIVE_ATTRIBUTES )

        print "GL_FLOAT_MAT4", GL_FLOAT_MAT4
        print "GL_FLOAT", GL_FLOAT
        print "GL_FLOAT_VEC4", GL_FLOAT_VEC4
        
        class VariableManager:
            program = self
            set_functions = {}
            def __setattr__( self, name, value ):
                self.set_functions[ name ]( program, value )

        for u in range( nuniforms ):
            name, size, data_type = glGetActiveUniform( self.program, u )
            loc = glGetUniformLocation( self.program, name )
            print "Uniform:", name, size, data_type, loc
            
            if data_type in ( GL_FLOAT_MAT4, ):
                def set_uniform_fn( self, data ):
                    fn = self.set_uniform[ data_type ]
                    fn( loc, size, False, data )

            elif size == 1:
                def set_uniform_fn( self, data ):
                    self.set_uniform[ data_type ][ 0 ]( loc, 1, *data )
                    
            else:
                def set_uniform_fn( self, data ):
                    self.set_uniform[ data_type ][ 1 ]( loc, size, data )
            #self.set_fns[ name ] = set_uniform_fn
            VariableManager.set_functions[ name ] = set_uniform_fn

        for a in range( nattribs ):
            length, name = GLsizei(0), c_char_p('\0'*100)
            data_type, size = GLuint(0), GLint(0)
            glGetActiveAttrib( self.program, a, 100, pointer(length), 
                    pointer(size), pointer(data_type), name )

            size, data_type, name = size.value, data_type.value, name.value
            loc = glGetAttribLocation( self.program, name )
            print "Attrib:", name, size, data_type, loc

            def set_attrib_fn( self, data ):
                print "set"
                if isinstance( data, self.VertexAttrib ):
                    #Will bind actual data later using glVertexAttribPointer
                    print "Bind temp."
                    size, data_type = self.set_attrib_ptr[ data_type ]
                    self.attrib_pointer[ data ] = ( loc, size, data_type ) 
                else:
                    #Otherwise assume we're just assigning one value
                    self.set_attrib[ data_type ]( loc, *data )
            #self.set_fns[ name ] = set_attrib_fn
            VariableManager.set_functions[ name ] = set_attrib_fn
        self.vars = VariableManager()

    def bind( self, data_type, data ):
        loc, size, data_type = self.attrib_pointer[ data_type ]
        glVertexAttribPointer( loc, size, data_type, False, 0, data )
    
    def apply( self ):
        glUseProgram( self.program )

    def __del__( self ):
        if( bool(glDeleteProgram) ):
            glDeleteProgram( self.program )

class Batch:
    Vertex = 0
    Color = 1

    def __init__( self, draws ):
        self.draws = draws
        self.vertex_buffer = None
        self.rebuild()

    def rebuild( self ):
        (self.nvertices, self.vertices, self.colors,
            self.nindices, self.indices) = self._generate_data( self.draws )

        if glGenBuffers:
            if not self.vertex_buffer:
                self.vertex_buffer, self.color_buffer = glGenBuffers( 2 )
                glBindBuffer( GL_ARRAY_BUFFER_ARB, self.vertex_buffer )
                glBufferData( GL_ARRAY_BUFFER_ARB, self.vertices,
                              GL_DYNAMIC_DRAW )

                glBindBuffer( GL_ARRAY_BUFFER_ARB, self.color_buffer )
                glBufferData( GL_ARRAY_BUFFER_ARB, self.colors,
                              GL_DYNAMIC_DRAW )

            else:
                glBindBuffer( GL_ARRAY_BUFFER_ARB, self.vertex_buffer )
                glBufferSubData( GL_ARRAY_BUFFER_ARB, 0, self.vertices )

                glBindBuffer( GL_ARRAY_BUFFER_ARB, self.color_buffer )
                glBufferSubData( GL_ARRAY_BUFFER_ARB, 0, self.colors )

    def draw( self, shader = None ):
        if glGenBuffers:
            glBindBuffer( GL_ARRAY_BUFFER_ARB, self.vertex_buffer )
            if shader is None:  glVertexPointer( 3, GL_FLOAT, 0, None )
            else:               shader.bind( shader.Vertex, None )

            glBindBuffer( GL_ARRAY_BUFFER_ARB, self.color_buffer )
            if shader is None:  glColorPointer( 4, GL_UNSIGNED_BYTE, 0, None )
            else:               shader.bind( shader.Color, None )
        else:
            glVertexPointer( 3, GL_FLOAT, 0, self.vertices )
            glColorPointer( 4, GL_UNSIGNED_BYTE, 0, self.colors )

        glEnableClientState( GL_VERTEX_ARRAY )
        glEnableClientState( GL_COLOR_ARRAY )

        glDrawElements( GL_TRIANGLES, self.nindices,
                GL_UNSIGNED_SHORT, self.indices )

        glDisableClientState( GL_VERTEX_ARRAY )
        glDisableClientState( GL_COLOR_ARRAY )

    def _generate_data( self, draws ):
        nv, ni = 0, 0
        for d in draws:
            d.set_offsets( nv, ni )
            nv, ni = nv + d.nvertices, ni + d.nindices

        def build( n, type, unpack_array, data ):
            iterator = chain.from_iterable( data )
            if unpack_array:
                iterator = chain.from_iterable( iterator )

            arr_type = type * n
            return arr_type( *iterator )

        v = build( nv * 3, GLfloat, True, (d.vertices() for d in draws) )
        c = build( nv * 4, GLubyte, True, (d.colors() for d in draws) )
        i = build( ni, GLushort, False, (d.indices() for d in draws) )

        return nv, v, c, ni, i
