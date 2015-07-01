
_Note: You can see the end result [here](sample.html) if you want to skip ahead._

While figuring out how to use WebGL as part of some other projects I got interested in rendering atmospheric scattering.  You can find a few reference on how to do this on the internet, but most of them were written before graphics cards were fast enough to run the entire calculation in real time on a GPU.  Since that's the age we now live in, it's pretty easy to get the entire thing working without have to precompute any tables or make any serious sacrifices in realism.  I've written a GLSL fragment shader that implements the entire calculation of atmospheric scattering from an Earth-like body and displays the result in a web page using Three.js and WebGL.


### Atmospheric Scattering Theory

There are two types of scattering that occur in the atmosphere and together they give rise to all of the colors the sky appears to us down here.  

1. Rayleigh scattering is very wavelength sensitive and makes the sun appear yellow (because blue is more strongly scattered) and the rest of the sky blue.
2. Mie scattering is wavelength insensitive and contributes mostly at shallow viewing angles to the horizon.

Rayleigh scattering occurs when light interacts with particles in the air that are much smaller than the wavelength of the light.  This means there is no phase shift over the surface of the scatterer and the behaviour of the scattered light won't have any dependence on the shape or orientation of the particles.  The scattering amplitude strongly depends on the wavelength of the light and is given by 

%{\large\[I(\lambda, \theta) = I_0(\lambda) \kappa \rho \frac{F(\theta)}{\lambda^4}\]}%

where $I_0$ is the incoming light intensity (usually from the sun), $\kappa$ controls the strength of the interaction, $\rho$ is the density of the scatterers (which is a function of height), $F$ is the scattering phase function, $\theta$ is the angle between the incoming light and the scattered light, and $\lambda$ is the wavelength of the scattered light.

Mie scattering is caused by aerosols and other relatively large particles in the air.  The size of the particles actually has a rather large effect on the scattering in this case, but we'll ignore that and just tune the constants to try tog et the average behavior to look pretty good.  The scattering amplitude is the same as above except without the $1/\lambda^4$ dependence, and with a different phase function.  For both Rayleigh and Mie scattering we'll use a modified Henyey-Greenstein function from [Nishita 93].

    #!glsl
    float phase( float cosangle, float g ) {
        return 1.5 * (1. - g*g) / (2. + g*g) *
            (1. + cosangle*cosangle) /
            pow( 1. + g*g - 2. * g * cosangle, 1.5 );
    }

The parameter cosangle is the cosine of $\theta$ defined above, and g is a parameter that describes the directivity of the scattered light. Positive g corresponds to forward scattering (not much change in angle at the scatterer), negative g the opposite, and small g corresponds to isotropic scattering.  Rayleigh scattering is mostly isotropic, while Mie scattering is forward directed.

### Equations

In order to approximate atmospheric scatter we need to approximate the integral of these scattering functions along a ray directed from our virtual camera.  For each pixel in the image we need to integrate the amount of light scattered towards the camera from each point in the atmosphere.  To solve for the scattered light's intensity we need to know $I_0$ the initial intensity of light that reaches that point in the atmosphere from the sun.  A simple assumption that yields acceptable results is that the particles for rayleigh and mie scatter are exponentially distributed in the atmosphere with different scale heights.  The Mie scale height is lower because the particles are larger and heavier.  Therefore, an approximation for the incoming light to a given point is:

%\large\[I_0(\lambda) = \exp \left( -\int_{P_{sun}}^{P_{scatter}} 4\pi k_{scatter}(\lambda) * \exp\left( -\frac{height}{scale\_height_{scatter}} \right) ds \right) \]%

where $k_{scatter}(\lambda)$ is a constant that is different for both mie and rayleigh scatter, and in the case of rayleigh scattering also depends on wavelength. Height is the height of the current sample in the atmosphere.  Here is the function that calculates the exponent.

    #!glsl
    // Calculate 1 / lambda^4 for red, green, and blue sample colors
    // We will multiply the base rayleigh scattering by these factors
    vec3 oolambda4 = vec3( 
        1.0 / pow( 0.650, 4. ),		// 650nm red
        1.0 / pow( 0.570, 4. ),		// 570nm green
        1.0 / pow( 0.475, 4. )		// 475nm blue
        );

    vec3 out_scatter( vec3 pos, vec3 dir ) {
        // Ray to sphere calculates the two intersection points
        // between a ray and a sphere as distances along the ray direction.
        Collision planet_inter = ray_to_sphere(pos, dir, planet_radius);

        // Return a large attenuation factor if light from the sun to
        // this position is occluded by the planet
        if( planet_inter.hit ) return vec3( 1000.0, 1000.0, 1000.0 );

        // Calculate where sun light enters the atmosphere to 
        // reach this point and set up finite steps to approximate
        // the scattering integral above.
        Collision atmos_inter = ray_to_sphere( pos, dir, atmos_radius );
        vec3 end = pos + dir * atmos_inter.t2;
        vec3 step = ( end - pos ) / float(nout_samples);
        float step_dist = length( step );
        vec3 sample = pos + step * 0.5;

        // Accumulate attenuation for all 3 sample colors.
        // Note that the mie scattering has no wavelength dependence
        vec3 result = vec3( 0. );
        for( int i = 0; i < nout_samples; ++i ) {
            float height = length( sample ) - planet_radius;
            result += step_dist * 
                (k_rayleigh_4pi * oolambda4 * 
                    exp( -height / rayleigh_scale_depth ) 
                k_mie_4pi * vec3( 1., 1., 1. ) *
                    exp( -height / mie_scale_depth ) );
            sample += step;
        }

        return result;
    }

Given the above function, it's easy to calculate the scattering contribution at any point in the atmosphere from the equations described previously.  In order to calculate the contribution of this scattered light to the final image we also need to attenuate it by the scattering that will happen on its way through the atmosphere from the sample point to the camera.  Finally, we need to approximate integrating those equations over every point in the atmosphere along a given ray going to the camera to calculate the final color contributed by atmospheric scattering.

%\large\[atten = \exp\left( -out\_scatter(P, P_{sun}-P) - out\_scatter(P, P_{camera}-P) \right)  ds \]%
%\large\[I_{out}(\lambda) = I_{sun}(\lambda) k_{scatter}(\lambda) F(\theta) \int_{P_{enter}}^{P_{exit}} \exp\left( -\frac{height}{scale\_height} \right) atten * ds \]%

    #!glsl
    vec4 atmos_sample( vec3 pos, vec3 dir ) {
        // Once again calculate intersection points to determine
        // where to integrate from and to
        Collision planet_inter = ray_to_sphere(pos, dir, planet_radius);
        Collision atmos_inter = ray_to_sphere( pos, dir, atmos_radius );

        if( !planet_inter.hit && !atmos_inter.hit )    discard;
        float start_t = 0.0;
        if( atmos_inter.t1 > 0. )    start_t = atmos_inter.t1;

        float end_t = atmos_inter.t2;
        if( planet_inter.hit )      end_t = planet_inter.t1;
        
        // Set up integration steps
        vec3 start = pos + dir * start_t;
        vec3 end = pos + dir * end_t;
        vec3 step = ( end - start ) / float(nsamples);
        float step_dist = length( step );
        vec3 sample = start + step * 0.5;

        // Implement the above integral
        vec3 rayleigh_integral = vec3(0.), mie_integral = vec3(0.);
        for( int i = 0; i < nsamples; ++i ) {
            float height = length( sample ) - planet_radius;
            vec3 loss_from_sun = out_scatter( sample, sun );
            vec3 loss_to_camera = out_scatter( sample, -dir );
            vec3 scale = exp( -loss_from_sun - loss_to_camera );
            rayleigh_integral += step_dist * scale *
                exp( -height / rayleigh_scale_depth );
            mie_integral += step_dist * scale *
                exp( -height / mie_scale_depth );
            sample += step;
        }

        // Calculate phase function and find final scattering result
        float cosangle = dot( sun, dir );
        return vec4(
            phase( cosangle, 0.0 ) * rayleigh_integral * 
                oolambda4 * k_rayleigh * E_sun +
            phase( cosangle, g ) * mie_integral * k_mie * E_sun, 
            1.0 );
    }

The final result involves just one more calculation.  Light scattered directly off the surface of the planet and then attenuated by the atmosphere on its journey to the camera must be added to the previous result.  The surface scattered light is calculated in a separate rendering pass and saved in an OpenGL texture to be passed to this calculation.

    #!glsl
    varying vec3 vDir;
    varying vec2 vUv;
    uniform sampler2D planet;

    void main() {
        // Calculate ray direction and its intersection point with the planet
        vec3 dir = normalize( vDir );
        vec3 offpos = camera_pos - planet_pos;
        Collision planet_inter = ray_to_sphere( 
            offpos, dir, planet_radius );

        // Calculate light scattered from planet and its attenuation
        vec4 planet_color = texture2D( planet, vUv );
        float inter = planet_inter.t1 - 0.001;
        vec3 scatter = out_scatter( offpos + dir * inter, -dir );
        vec4 atten = vec4( exp( -scatter ), 1.0 );

        // Add light scattered from planet and light scattered in atmosphere
        gl_FragColor = atmos_sample( offpos, dir ) + 
            planet_color * atten;
    }

### Techniques

Now that we have the shader written, we just have to perform a bit of work with Three.js to set things up to use it.  We need to find the rays coming from the camera taht we need to integrate along, and we need to calculcate the scattering directly off the planet and save that in a texture to use in the atmosphere calculations.

    #!javascript
    function Atmosphere( planet, base_camera ) {
        this.planet = planet;
        this.planet_scene = new THREE.Scene();
        this.planet_scene.add( planet.mesh );

        // Light the planet with a directional white light
        this.sun = new THREE.DirectionalLight( 0xffffff, 1 );
        this.sun.position.set( 0.707, 0.707, 0 );
        this.planet_scene.add( this.sun );

        // Create a camera to render the planet with and attach it to the
        // main camera so it will move with it
        this.planet_camera = new THREE.PerspectiveCamera(
            75., window.innerWidth / window.innerHeight, 1e3, 1e8 );
        base_camera.add( this.planet_camera );

        // Create a texture to save the rendered planet to pass to the
        // atmosphere calculations
        this.planet_texture = new THREE.WebGLRenderTarget(
            window.innerWidth, window.innerHeight, {
                minFilter: THREE.LinearFilter,
                magFilter: THREE.NearestFilter,
                format: THREE.RGBFormat 
            } );

        // We will unproject these vectors in projection space each frame
        // to calculate the directions of rays coming out of each pixel
        // of the camera
        this.base_directions = [
            new THREE.Vector3( -1, 1, 0.5 ), new THREE.Vector3( 1, 1, 0.5 ),
            new THREE.Vector3( -1, -1, 0.5 ), new THREE.Vector3( 1, -1, 0.5 )];
        this.directions = [
            new THREE.Vector3( -1, 1, 0.5 ), new THREE.Vector3( 1, 1, 0.5 ),
            new THREE.Vector3( -1, -1, 0.5 ), new THREE.Vector3( 1, -1, 0.5 )];

        // The atmosphere will be rendered on a fullscreen plane and our glsl 
        // code above will be run in the fragment shader so that the 
        // calculations occur for every pixel in the image.
        var plane = new THREE.PlaneGeometry( 
            window.innerWidth, window.innerHeight );

        this.rayleigh_length = 7.64e3;
        this.rayleigh_constant = 0.0025;
        this.mie_length = 2e3;
        this.mie_constant = 0.0015;
        this.radius = planet.radius + this.rayleigh_length * 5;

        this.uniforms = {
            camera_pos: { type: 'v3', value: new THREE.Vector3() },
            planet_pos: { type: 'v3', value: new THREE.Vector3() },
            planet_radius: { type: 'f', value: 0.0 },
            atmos_radius: { type: 'f', value: 0.0 },

            rayleigh_scale_depth: { type: 'f', value: this.rayleigh_length },
            k_rayleigh: { type: 'f', value: this.rayleigh_constant },
            mie_scale_depth: { type: 'f', value: this.mie_length },
            k_mie: { type: 'f', value: this.mie_constant },

            planet: { type: 't', value: this.planet_texture },
            sun: { type: 'v3', value: this.sun.position }
        }
        this.attributes = {
            sampleDir: { type: 'v3', value: this.directions }
        }

        var material = new THREE.ShaderMaterial( {
            uniforms: this.uniforms,
            attributes: this.attributes,
            vertexShader: atmosVertex,
            fragmentShader: atmosFragment } );

        this.mesh = new THREE.Mesh( plane, material );
        this.mesh.position.z = -9999;

        this.scene = new THREE.Scene();
        this.scene.add( this.mesh );

        this.camera = new THREE.OrthographicCamera( 
            window.innerWidth / -2, window.innerWidth / 2,
            window.innerHeight / 2, window.innerHeight / -2, -10000, 10000 );
        this.time = 0;
    }

    Atmosphere.prototype.render = function ( renderer ) {
        // Unproject our projection space positions and then subtract the
        // camera position to get view directions
	    var offset = new THREE.Vector3();
        for( var i = 0; i < 4; ++i ) {
            offset.setFromMatrixPosition( this.planet_camera.matrixWorld );
            this.directions[i].copy( this.base_directions[i] );
            this.directions[i].unproject( this.planet_camera );
            this.directions[i].sub( offset );
        }
        this.attributes.sampleDir.needsUpdate = true;

        // Rotate the sun around the planet as a cheap hack
        this.sun.position.set( Math.cos( Date.now() / 5000 ), 
            0, Math.sin( Date.now() / 5000 ) ).normalize();

        var scale = 1e-5
        this.radius = this.planet.radius + this.rayleigh_length * 5;
        this.uniforms.camera_pos.value.setFromMatrixPosition(
            this.planet_camera.matrixWorld ).multiplyScalar( scale );
        this.uniforms.planet_pos.value.copy( this.planet.mesh.position ).
            multiplyScalar( scale );
        this.uniforms.planet_radius.value = this.planet.radius * 0.999*scale;
        this.uniforms.atmos_radius.value = this.radius * scale;

        this.uniforms.rayleigh_scale_depth.value = this.rayleigh_length * scale;
        this.uniforms.k_rayleigh.value = this.rayleigh_constant;
        this.uniforms.mie_scale_depth.value = this.mie_length * scale;
        this.uniforms.k_mie.value = this.mie_constant;

        // Render the planet to its texture then render the atmosphere
        renderer.render( this.planet_scene, this.planet_camera,
            this.planet_texture, true );
        renderer.render( this.scene, this.camera );
    }

The end result can be seen [here](sample.html) if your browser supports WebGL.  One of these days I'm planning to add some volumetric clouds to it to improve the realism a little bit.  Calculating the scattering every frame also definitely sacrifices some performance, and precomuting a few simple things would improve the rendering speed without signifcant sacrifices in realism.  In particular, the out\_scatter function could be replaced by a precomputed texture as a function of $\theta$ and height.  For the time being I'm happy with the result.

### References

 Nishita, T., T. Sirai, K. Tadamura, and E. Nakamae. 1993. "Display of the Earth Taking into Account Atmospheric Scattering." In _Proceedings of SIGGRAPH 93_, pp. 175–182. [http://nis-lab.is.s.u-tokyo.ac.jp/~nis/cdrom/sig93\_nis.pdf](http://nis-lab.is.s.u-tokyo.ac.jp/~nis/cdrom/sig93_nis.pdf)

