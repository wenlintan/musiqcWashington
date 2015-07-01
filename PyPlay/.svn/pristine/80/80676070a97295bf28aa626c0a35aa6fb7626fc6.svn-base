
<!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
 <head>
  <title>/branches/Lamina/lamina.pyPitchers Duel</title>
  <link rel="search" href="/search" />
  <link rel="help" href="/wiki/TracGuide" />
  <link rel="alternate" href="/file/branches/Lamina/lamina.py?rev=433&amp;format=raw" title="Original Format" type="text/x-python" />
  <link rel="alternate" href="/file/branches/Lamina/lamina.py?rev=433&amp;format=txt" title="Plain Text" type="text/plain" />
  <link rel="up" href="/browser/branches/Lamina/" title="Parent directory" />
  <link rel="start" href="/wiki" />
  <link rel="shortcut icon" href="/trac/trac.ico" type="image/x-icon" />
  <link rel="icon" href="/trac/trac.ico" type="image/x-icon" />
  <style type="text/css">
   @import url(/trac/css/trac.css);
   @import url(/trac/css/browser.css);
   

  </style>
  <script src="/trac/trac.js" type="text/javascript"></script>
 </head>
<body>


<div id="banner">

<div id="header">
  <a id="logo" href="/"><img src="/trac/logo.jpg"/></a>
  <hr />
</div>

<form id="search" action="/search" method="get">
 <div>
  <label for="proj-search">Search:</label>
  <input type="text" id="proj-search" name="q" size="10" value="" />
  <input type="submit" value="Search" />
  <input type="hidden" name="wiki" value="on" />
  <input type="hidden" name="changeset" value="on" />
  <input type="hidden" name="ticket" value="on" />
 </div>
</form>

<div id="metanav" class="nav">
 <h2>Navigation</h2>
 <ul>
  <li class="first">
    <a href="/login">Login</a>
  </li>
  <li><a href="/settings">Settings</a></li>
  <li><a accesskey="6" href="/wiki/TracGuide">Help/Guide</a></li>
  <li style="display: none"><a accesskey="5" href="http://projects.edgewall.com/trac/wiki/TracFaq">FAQ</a></li>
  <li style="display: none"><a accesskey="0" href="/wiki/TracAccessibility">Accessibility</a></li>
  <li class="last"><a accesskey="9" href="/about_trac">About Trac</a></li>
 </ul>
</div>

</div>





<div id="mainnav" class="nav">
 <ul>
  <li><a href="/wiki" accesskey="1">Wiki</a></li>
  <li><a href="/timeline" accesskey="2">Timeline</a></li>
  <li><a href="/roadmap" accesskey="3">Roadmap</a></li>
  <li><a href="/browser/" class="active">Browse Source</a></li>
  <li><a href="/report">View Tickets</a></li>
  
  <li><a href="/search" accesskey="4">Search</a></li>
 </ul>
</div>

<div id="main">
















<div id="ctxtnav" class="nav">
 <ul>
  <li class="last"><a href="/log/branches/Lamina/lamina.py?rev=433">Revision Log</a></li>
 </ul>
</div>

<div id="content" class="file">

 
  
 <h1><a class="first" title="Go to root directory" href="/browser/">root</a><span class="sep">/</span><a title="Go to directory" href="/browser/branches/">branches</a><span class="sep">/</span><a title="Go to directory" href="/browser/branches/Lamina/">Lamina</a><span class="sep">/</span><span class="filename">lamina.py</span></h1>

  <div id="jumprev">
   <form action="" method="get">
    <div>
     <label for="rev">View revision:</label>
     <input type="text" id="rev" name="rev" value="433" size="4" />
    </div>
   </form>
  </div>
  <table id="info" summary="Revision info">
   <tr>
    <th scope="row">
     Revision <a href="/changeset/433">433</a>
     (by dkeeney, 01/21/08 20:33:14)
    </th>
    <td class="message"><p>
fix memory leak.  'clear' now deletes old texture (using 'regen' method) before creating new.
</p>
</td>
   </tr>
  </table>
 

 <div id="preview">
  
   <div class="code-block"><PRE>
<span class="code-string"><B>&quot;&quot;&quot;
Lamina module

When you set the display mode for OpenGL, you enable all the coolness of 3D rendering, 
but you disable the bread-and-butter raster SDL functionality like fill() and blit(). 
Since the GUI libraries use those surface methods extensively, they cannot readily be 
used in OpenGL displays.

Lamina provides the LaminaPanelSurface and LaminaScreenSurface classes, which bridge 
between the two.

The 'surf' attribute is a surface, and can be drawn on, blitted to, and passed to GUI 
rendering functions for alteration. The 'display' method displays the surface as a 
transparent textured quad in the OpenGL model-space. The 'refresh' method indicates that 
the surface has changed, and that the texture needs regeneration. The 'clear' method 
restores the blank and transparent original condition.

Usage is vaguely like this incomplete pseudocode:
    
    # create gui with appropriate constructor
    gui = GUI_Constructor()
    
    # create LaminaPanelSurface
    gui_screen = lamina.LaminaPanelSurface( (640,480), (-1,1,2,2) )

    # draw widgets on surface
    gui.draw( gui_screen.surf ) 

    # hide mouse cursor
    pygame.mouse.set_visible(0)
    
    while 1:
        
        # do input events ....
        # pass events to gui
        gui.doevent(...)

        # detect changes to surface
        changed = gui.update( gui_screen.surf )
        if changed:            
            # and mark for update
            gui_screen.refresh()   

        # draw opengl geometry .....

        # display gui
        # opengl code to set modelview matrix for desired gui surface pos
        gui_screen.display()


If your gui screen is not sized to match the display, hide the system 
mouse cursor, and use the convertMousePos method to position your own
OpenGL mouse cursor (a cone or something).  The result of the 
convertMousePos is 2D, (x,y) so you need to draw the mouse with the same
modelview matrix as drawing the LaminaPanelSurface itself.        
        
        mouse_pos = gui_screen.convertMousePos(mouseX, mouseY)
        glTranslate(*mouse_pos)
        # opengl code to display your mouse object (a cone?)
        
        
The distribution package includes several demo scripts which are functional.  Refer
to them for details of working code.
&quot;&quot;&quot;</span></B>

<B><span class="code-lang">import</span></B> OpenGL.GLU as oglu
<B><span class="code-lang">import</span></B> OpenGL.GL as ogl

<B><span class="code-lang">import</span></B> pygame
<B><span class="code-lang">import</span></B> math

<B><span class="code-lang">def</span></B> <B><span class="code-func">load_texture</span></B>(surf):
    <span class="code-string"><B>&quot;&quot;&quot;Load surface into texture object. Return texture object. 
    @param surf: surface to make texture from.
    &quot;&quot;&quot;</span></B>
    txtr = ogl.glGenTextures(1)
    textureData = pygame.image.tostring(surf, <span class="code-string"><B>&quot;RGBA&quot;</span></B>, 1)

    ogl.glEnable(ogl.GL_TEXTURE_2D)
    ogl.glBindTexture(ogl.GL_TEXTURE_2D, txtr)
    width, height = surf.get_size()
    ogl.glTexImage2D( ogl.GL_TEXTURE_2D, 0, ogl.GL_RGBA, width, height, 0, 
      ogl.GL_RGBA, ogl.GL_UNSIGNED_BYTE, textureData )
    ogl.glTexParameterf(ogl.GL_TEXTURE_2D, ogl.GL_TEXTURE_MAG_FILTER, ogl.GL_NEAREST)
    ogl.glTexParameterf(ogl.GL_TEXTURE_2D, ogl.GL_TEXTURE_MIN_FILTER, ogl.GL_NEAREST)
    ogl.glDisable(ogl.GL_TEXTURE_2D)
    <B><span class="code-lang">return</span></B> txtr

<B><span class="code-lang">def</span></B> <B><span class="code-func">overlay_texture</span></B>(txtr, surf, r):
    <span class="code-string"><B>&quot;&quot;&quot;Load surface into texture object, replacing part of txtr
    given by rect r. 
    @param txtr: texture to add to
    @param surf: surface to copy from
    @param r: rectangle indicating area to overlay.
    &quot;&quot;&quot;</span></B>
    subsurf = surf.subsurface(r)
    textureData = pygame.image.tostring(subsurf, <span class="code-string"><B>&quot;RGBA&quot;</span></B>, 1) 

    hS, wS = surf.get_size()
    rect = pygame.Rect(r.x,hS-(r.y+r.height),r.width,r.height)
    
    ogl.glEnable(ogl.GL_TEXTURE_2D)
    ogl.glBindTexture(ogl.GL_TEXTURE_2D, txtr)
    ogl.glTexSubImage2D(ogl.GL_TEXTURE_2D, 0, rect.x, rect.y, rect.width, rect.height,  
      ogl.GL_RGBA, ogl.GL_UNSIGNED_BYTE, textureData )
    ogl.glDisable(ogl.GL_TEXTURE_2D)

<B><span class="code-lang">class</span></B> LaminaPanelSurface(object): 
    <span class="code-string"><B>&quot;&quot;&quot;Surface for imagery to overlay. 
    @ivar surf: surface
    @ivar dims: tuple with corners of quad
    &quot;&quot;&quot;</span></B>

    <B><span class="code-lang">def</span></B> <B><span class="code-func">__init__</span></B>(self, quadDims=(-1,-1,2,2), winSize=None):
        <span class="code-string"><B>&quot;&quot;&quot;Initialize new instance. 
        @param winSize: tuple (width, height)
        @param quadDims: tuple (left, top, width, height)
        &quot;&quot;&quot;</span></B>
        <B><span class="code-lang">if</span></B> <B><span class="code-lang">not</span></B> winSize:
            winSize = pygame.display.get_surface().get_size()
        self._txtr = None
        self._winSize = winSize
        left, top, width, height = quadDims
        right, bottom = left+width, top-height
        self._qdims = quadDims
        self.dims = (left,top,0), (right,top,0), (right,bottom,0), (left,bottom,0) 
        self.clear()
        
    <B><span class="code-lang">def</span></B> <B><span class="code-func">clear</span></B>(self):
        <span class="code-string"><B>&quot;&quot;&quot;Restore the total transparency to the surface. &quot;&quot;&quot;</span></B>
        powerOfTwo = 64
        <B><span class="code-lang">while</span></B> powerOfTwo &lt; max(*self._winSize):
            powerOfTwo *= 2
        raw = pygame.Surface((powerOfTwo, powerOfTwo), pygame.SRCALPHA, 32)
        self._surfTotal = raw.convert_alpha()
        self._usable = 1.0*self._winSize[0]/powerOfTwo, 1.0*self._winSize[1]/powerOfTwo
        self.surf = self._surfTotal.subsurface(0,0,self._winSize[0],self._winSize[1])
        self.regen()
    
    <B><span class="code-lang">def</span></B> <B><span class="code-func">regen</span></B>(self):
        <span class="code-string"><B>&quot;&quot;&quot;Force regen of texture object. Call after change to the GUI appearance. &quot;&quot;&quot;</span></B>
        <B><span class="code-lang">if</span></B> self._txtr:
            ogl.glDeleteTextures([self._txtr])
        self._txtr = None

    <B><span class="code-lang">def</span></B> <B><span class="code-func">refresh</span></B>(self, dirty=None):
        <span class="code-string"><B>&quot;&quot;&quot;Refresh the texture from the surface. 
        @param dirty: list of rectangles to update, None for whole panel
        &quot;&quot;&quot;</span></B>
        <B><span class="code-lang">if</span></B> <B><span class="code-lang">not</span></B> self._txtr:
            self._txtr = load_texture(self._surfTotal)
        <B><span class="code-lang">else</span></B>:
            wS, hS = self._surfTotal.get_size()
            <B><span class="code-lang">if</span></B> dirty <B><span class="code-lang">is</span></B> None:
                dirty = [pygame.Rect(0,0,wS,hS)]
            <B><span class="code-lang">for</span></B> r <B><span class="code-lang">in</span></B> dirty:
                overlay_texture(self._txtr,self._surfTotal,r)
                
    <B><span class="code-lang">def</span></B> <B><span class="code-func">convertMousePos</span></B>(self, pos):
        <span class="code-string"><B>&quot;&quot;&quot;Converts 2d pixel mouse pos to 2d gl units. 
        @param pos: 2-tuple with x,y of mouse
        &quot;&quot;&quot;</span></B>
        x0, y0 = pos
        x = x0/self._winSize[0]*self._qdims[2] + self._qdims[0]
        y = y0/self._winSize[1]*self._qdims[3] + self._qdims[1]
        <B><span class="code-lang">return</span></B> x, y
    
    <B><span class="code-lang">def</span></B> <B><span class="code-func">display</span></B>(self):
        <span class="code-string"><B>&quot;&quot;&quot;Draw surface to a quad. Call as part of OpenGL rendering code.&quot;&quot;&quot;</span></B>
        ogl.glEnable(ogl.GL_BLEND)
        ogl.glBlendFunc(ogl.GL_SRC_ALPHA, ogl.GL_ONE_MINUS_SRC_ALPHA)  
        ogl.glEnable(ogl.GL_TEXTURE_2D)
        ogl.glBindTexture(ogl.GL_TEXTURE_2D, self._txtr)
        ogl.glTexEnvf(ogl.GL_TEXTURE_ENV, ogl.GL_TEXTURE_ENV_MODE, ogl.GL_REPLACE)
        
        ogl.glBegin(ogl.GL_QUADS)
        ogl.glTexCoord2f(0.0, 1.0)
        ogl.glVertex3f(*self.dims[0])
        ogl.glTexCoord2f(self._usable[0], 1.0)
        ogl.glVertex3f(*self.dims[1])
        ogl.glTexCoord2f(self._usable[0], 1-self._usable[1])
        ogl.glVertex3f(*self.dims[2])
        ogl.glTexCoord2f(0.0, 1-self._usable[1])
        ogl.glVertex3f(*self.dims[3])
        ogl.glEnd()
        ogl.glDisable(ogl.GL_BLEND)
        ogl.glDisable(ogl.GL_TEXTURE_2D)
        
    <B><span class="code-lang">def</span></B> <B><span class="code-func">testMode</span></B>(self):
        <span class="code-string"><B>&quot;&quot;&quot;Draw red/transparent checkerboard. &quot;&quot;&quot;</span></B>
        w, h = self._winSize[0]*0.25, self._winSize[1]*0.25
        Rect = pygame.Rect
        pygame.draw.rect(self.surf, (250,0,0), Rect(0,0,w,h), 0)
        pygame.draw.rect(self.surf, (250,0,0), Rect(2*w,0,w,h), 0)
        
        pygame.draw.rect(self.surf, (250,0,0), Rect(w,h,w,h), 0)
        pygame.draw.rect(self.surf, (250,0,0), Rect(3*w,h,w,h), 0)
        
        pygame.draw.rect(self.surf, (250,0,0), Rect(0,2*h,w,h), 0)
        pygame.draw.rect(self.surf, (250,0,0), Rect(2*w,2*h,w,h), 0)
        
        pygame.draw.rect(self.surf, (250,0,0), Rect(w,3*h,w,h), 0)
        pygame.draw.rect(self.surf, (250,0,0), Rect(3*w,3*h,w,h), 0)
        self.clear = None


<B><span class="code-lang">class</span></B> LaminaScreenSurface(LaminaPanelSurface): 
    <span class="code-string"><B>&quot;&quot;&quot;Surface for imagery to overlay.  Autofits to actual display. 
    @ivar surf: surface
    @ivar dims: tuple with corners of quad
    &quot;&quot;&quot;</span></B>

    <B><span class="code-lang">def</span></B> <B><span class="code-func">__init__</span></B>(self, depth=0):
        <span class="code-string"><B>&quot;&quot;&quot;Initialize new instance. 
        @param depth: (0-1) z-value, if you want to draw your own 3D
        cursor, set this to a small non-zero value to allow room in 
        front of this overlay to draw the cursor. (0.1 is a first guess)
        &quot;&quot;&quot;</span></B>
        self._txtr = None
        self._depth = depth
        self.setup()

    <B><span class="code-lang">def</span></B> <B><span class="code-func">setup</span></B>(self):
        <span class="code-string"><B>&quot;&quot;&quot;Setup stuff, after pygame is inited. &quot;&quot;&quot;</span></B>
        self._winSize = pygame.display.get_surface().get_size()
        self.refreshPosition()
        self.clear()
        
    <B><span class="code-lang">def</span></B> <B><span class="code-func">refreshPosition</span></B>(self):
        <span class="code-string"><B>&quot;&quot;&quot;Recalc where in modelspace quad needs to be to fill screen.&quot;&quot;&quot;</span></B>
        depth = self._depth
        bottomleft = oglu.gluUnProject(0, 0, depth)
        bottomright = oglu.gluUnProject(self._winSize[0], 0, depth)
        topleft = oglu.gluUnProject(0, self._winSize[1], depth)
        topright = oglu.gluUnProject(self._winSize[0], self._winSize[1], depth)
        self.dims = topleft, topright, bottomright, bottomleft 
        width = topright[0] - topleft[0]
        height = topright[1] - bottomright[1]
        self._qdims = topleft[0], topleft[1], width, height
        

<B><span class="code-lang">class</span></B> LaminaScreenSurface2(LaminaScreenSurface):
    <span class="code-string"><B>&quot;&quot;&quot;Surface that defers initialization to setup method. &quot;&quot;&quot;</span></B>
    
    <B><span class="code-lang">def</span></B> <B><span class="code-func">__init__</span></B>(self, depth=0):
        <span class="code-string"><B>&quot;&quot;&quot;Initialize new instance. &quot;&quot;&quot;</span></B>
        self._txtr = None
        self._depth = depth        

    <B><span class="code-lang">def</span></B> <B><span class="code-func">refreshPosition</span></B>(self):
        <span class="code-string"><B>&quot;&quot;&quot;Recalc where in modelspace quad needs to be to fill screen.&quot;&quot;&quot;</span></B>
        self._dirty = True
        self._qdims = None, None
     
    <B><span class="code-lang">def</span></B> <B><span class="code-func">getPoint</span></B>(self, pt):
        <span class="code-string"><B>&quot;&quot;&quot;Get x,y coords of pt in 3d space.&quot;&quot;&quot;</span></B>
        pt2 = oglu.gluProject(*pt)
        <B><span class="code-lang">return</span></B> int(pt2[0]), int(pt2[1]), pt2[2]
     
    <B><span class="code-lang">def</span></B> <B><span class="code-func">update</span></B>(self):
        <B><span class="code-lang">pass</span></B>
        
    <B><span class="code-lang">def</span></B> <B><span class="code-func">commit</span></B>(self):
        <B><span class="code-lang">pass</span></B>
        
    <B><span class="code-lang">def</span></B> <B><span class="code-func">display</span></B>(self):
        <span class="code-string"><B>&quot;&quot;&quot;Display texture. &quot;&quot;&quot;</span></B>
        <B><span class="code-lang">if</span></B> self._dirty:
            depth = self._depth
            topleft = oglu.gluUnProject(0,self._winSize[1],depth)
            <B><span class="code-lang">assert</span></B> topleft, topleft
            <B><span class="code-lang">if</span></B> topleft[0:2] != self._qdims[0:2]:
                bottomleft = oglu.gluUnProject(0,0,depth)
                bottomright = oglu.gluUnProject(self._winSize[0],0,depth)
                topright = oglu.gluUnProject(self._winSize[0],self._winSize[1],depth)
                self.dims = topleft, topright, bottomright, bottomleft 
                width = topright[0] - topleft[0]
                height = topright[1] - bottomright[1]
                self._qdims = topleft[0], topleft[1], width, height
        LaminaScreenSurface.display(self)


<B><span class="code-lang">class</span></B> LaminaScreenSurface3(LaminaScreenSurface):
    <span class="code-string"><B>&quot;&quot;&quot;Surface that accepts a 3d point to constructor, and
    locates surface parallel to screen through given point.
    
    Defers initialization to setup method, like LSS2. 
    &quot;&quot;&quot;</span></B>
    
    <B><span class="code-lang">def</span></B> <B><span class="code-func">__init__</span></B>(self, point=(0,0,0)):
        <span class="code-string"><B>&quot;&quot;&quot;Initialize new instance. &quot;&quot;&quot;</span></B>
        self._txtr = None
        self._point = point        
        self._depth = None

    <B><span class="code-lang">def</span></B> <B><span class="code-func">refreshPosition</span></B>(self):
        <span class="code-string"><B>&quot;&quot;&quot;Recalc where in modelspace quad needs to be to fill screen.&quot;&quot;&quot;</span></B>
        self._dirty = True

    <B><span class="code-lang">def</span></B> <B><span class="code-func">getPoint</span></B>(self, pt):
        <span class="code-string"><B>&quot;&quot;&quot;Get x,y coords of pt in 3d space.&quot;&quot;&quot;</span></B>
        pt2 = oglu.gluProject(*pt)
        <B><span class="code-lang">return</span></B> pt2[0], pt2[1]
     
    <B><span class="code-lang">def</span></B> <B><span class="code-func">update</span></B>(self):
        <B><span class="code-lang">pass</span></B>
        
    <B><span class="code-lang">def</span></B> <B><span class="code-func">commit</span></B>(self):
        <B><span class="code-lang">pass</span></B>
        
    <B><span class="code-lang">def</span></B> <B><span class="code-func">display</span></B>(self):
        <span class="code-string"><B>&quot;&quot;&quot;Display texture. &quot;&quot;&quot;</span></B>
        <B><span class="code-lang">if</span></B> self._dirty:
            depth = oglu.gluProject(*self._point)[2]
            <B><span class="code-lang">if</span></B> depth != self._depth:
                bottomleft = oglu.gluUnProject(0,0,depth)
                bottomright = oglu.gluUnProject(self._winSize[0],0,depth)
                topleft = oglu.gluUnProject(0,self._winSize[1],depth)
                topright = oglu.gluUnProject(self._winSize[0],self._winSize[1],depth)
                self.dims = topleft, topright, bottomright, bottomleft 
                width = topright[0] - topleft[0]
                height = topright[1] - bottomright[1]
                self._qdims = topleft[0], topleft[1], width, height
                self._depth = depth
        LaminaScreenSurface.display(self)
</PRE></div>
  
 </div>

 

 
  <div id="help">
   <strong>Note:</strong> See <a href="/wiki/TracBrowser">TracBrowser</a> for help on using the browser.
  </div>
 


</div>

<script type="text/javascript">searchHighlight()</script>


<div id="altlinks">
 <h3>Download in other formats:</h3>
 <ul>
  <li class="first">
   <a href="/file/branches/Lamina/lamina.py?rev=433&amp;format=raw">Original Format</a>
  </li>
  <li class="last">
   <a href="/file/branches/Lamina/lamina.py?rev=433&amp;format=txt">Plain Text</a>
  </li>
 </ul>
</div>


</div>

<div id="footer">
 <hr />
 <a id="tracpowered" href="http://trac.edgewall.com/"><img src="/trac/trac_logo_mini.png" height="30" width="107"
     alt="Trac Powered"/></a>
 <p class="left">
  Powered by <a href="/about_trac"><strong>Trac 0.8</strong></a><br />
  By <a href="http://www.edgewall.com/">Edgewall Software</a>.
 </p>
 <p class="right">
  Visit the Trac open source project at<br /><a href="http://trac.edgewall.com/">http://trac.edgewall.com/</a>
 </p>
</div>




 </body>
</html>

