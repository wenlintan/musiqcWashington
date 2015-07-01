
from OpenGL.GL import *
from OpenGL.GL.shaders import * 
from OpenGL.GL.framebufferobjects import *

from ctypes import *


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
