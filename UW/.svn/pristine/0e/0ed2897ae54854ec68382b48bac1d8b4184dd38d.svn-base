define(function() {
    function SimplePlanet( scene ) {
        this.mass = 5.972e24;
        this.radius = 6371e3;
        this.atmos_scale_height = 7.64e3;

        this.mesh = new THREE.Mesh(
          new THREE.SphereGeometry( this.radius, 64, 64 ),
          new THREE.MeshPhongMaterial({
            map: THREE.ImageUtils.loadTexture('images/2_no_clouds_8k.jpg'),
            bumpMap: THREE.ImageUtils.loadTexture('images/elev_bump_8k.jpg'),
            bumpScale:   0.005,
            specularMap: THREE.ImageUtils.loadTexture('images/water_8k.png'),
            })
        );

        this.position = new THREE.Vector3();
        this.position.set( 0, 0, -10e6 );
        this.mesh.position.copy( this.position );
        scene.add( this.mesh );
    }

    atmosVertex = [
        'attribute vec3 sampleDir;',
        'varying vec3 vDir;',
        'varying vec2 vUv;',
        'void main() {',
            'vUv = uv;',
            'vDir = sampleDir;',
            'gl_Position = projectionMatrix * ',
                'modelViewMatrix * vec4( position, 1.0 );',
        '}'].join( '\n' );

    atmosFragment = [
        'vec3 oolambda4 = vec3( ',
            '1.0 / pow( 0.650, 4. ),		// 650nm red',
            '1.0 / pow( 0.570, 4. ),		// 570nm green',
            '1.0 / pow( 0.475, 4. )		// 475nm blue',
            ');',

        'uniform float rayleigh_scale_depth;',
        'uniform float mie_scale_depth;',

        'const float pi = 3.141592654;',
        'uniform float k_rayleigh, k_mie;',
        'float k_rayleigh_4pi = k_rayleigh * 4.0 * pi, ',
            'k_mie_4pi = k_mie * 4.0 * pi;',

        'const float E_sun = 15.0;',
        'const float g = 0.75;',

        'const int nsamples = 4, nout_samples = 10;',
        'uniform float atmos_radius, planet_radius;',
        'uniform vec3 planet_pos;',
        'uniform vec3 camera_pos;',
        'uniform vec3 sun;',

        'struct Collision {',
            'bool hit;',
            'float t1, t2;',
        '};',

        'Collision ray_to_sphere( vec3 start, ',
            'vec3 dir, float radius ) {',

            'float b = 2.0 * dot( start, dir );',
            'float c = dot( start, start ) - radius * radius;',

            'float det = b*b - 4.0 * c;',
            'if( det < 0. )',
                'return Collision( false, 0., 0. );',

            'float sqdet = sqrt(det);',
            'float t2 = 0.5 * ( -b + sqdet );',
            'return Collision( t2 > 0., 0.5 * ( -b - sqdet ), t2 );',
        '}',

        'float phase( float cosangle, float g ) {',
            'return 1.5 * (1. - g*g) / (2. + g*g) *',
                '(1. + cosangle*cosangle) /',
                'pow( 1. + g*g - 2. * g * cosangle, 1.5 );',
        '}',


        'vec3 out_scatter( vec3 pos, vec3 dir ) {',
            'Collision planet_inter = ray_to_sphere(pos, dir, planet_radius);',
            'if( planet_inter.hit ) return vec3( 1000.0, 1000.0, 1000.0 );',

            'Collision atmos_inter = ray_to_sphere( pos, dir, atmos_radius );',
            'vec3 end = pos + dir * atmos_inter.t2;',
            'vec3 step = ( end - pos ) / float(nout_samples);',
            'float step_dist = length( step );',
            'vec3 sample = pos + step * 0.5;',

            'vec3 result = vec3( 0. );',
            'for( int i = 0; i < nout_samples; ++i ) {',
                'float height = length( sample ) - planet_radius;',
                'result += step_dist * ',
                    '(k_rayleigh_4pi * oolambda4 * ',
                        'exp( -height / rayleigh_scale_depth ) + ',
                    'k_mie_4pi * vec3( 1., 1., 1. ) *',
                        'exp( -height / mie_scale_depth ) );',
                'sample += step;',
            '}',

            'return result;',
        '}',

        'vec4 atmos_sample( vec3 pos, vec3 dir ) {',
            'Collision planet_inter = ray_to_sphere(pos, dir, planet_radius);',
            'Collision atmos_inter = ray_to_sphere( pos, dir, atmos_radius );',

            'if( !planet_inter.hit && !atmos_inter.hit )    discard;',
            'float start_t = 0.0;',
            'if( atmos_inter.t1 > 0. )    start_t = atmos_inter.t1;',

            'float end_t = atmos_inter.t2;',
            'if( planet_inter.hit )      end_t = planet_inter.t1;',
            
            'vec3 start = pos + dir * start_t;',
            'vec3 end = pos + dir * end_t;',
            'vec3 step = ( end - start ) / float(nsamples);',
            'float step_dist = length( step );',
            'vec3 sample = start + step * 0.5;',

            'vec3 rayleigh_integral = vec3(0.), mie_integral = vec3(0.);',
            'for( int i = 0; i < nsamples; ++i ) {',
                'float height = length( sample ) - planet_radius;',
                'vec3 loss_from_sun = out_scatter( sample, sun );',
                'vec3 loss_to_camera = out_scatter( sample, -dir );',
                'vec3 scale = exp( -loss_from_sun - loss_to_camera );',
                'rayleigh_integral += step_dist * scale *',
                    'exp( -height / rayleigh_scale_depth );',
                'mie_integral += step_dist * scale *',
                    'exp( -height / mie_scale_depth );',
                'sample += step;',
            '}',

            'float cosangle = dot( sun, dir );',
            'return vec4(',
                'phase( cosangle, 0.0 ) * rayleigh_integral * ',
                    'oolambda4 * k_rayleigh * E_sun +',
                'phase( cosangle, g ) * mie_integral * k_mie * E_sun, ',
                '1.0 );',
        '}',

        'varying vec3 vDir;',
        'varying vec2 vUv;',
        'uniform sampler2D planet;',

        'void main() {',
            'vec3 dir = normalize( vDir );',
            'vec3 offpos = camera_pos - planet_pos;',
            'Collision planet_inter = ray_to_sphere( ',
                'offpos, dir, planet_radius );',
            'vec4 planet_color = texture2D( planet, vUv );',
            'float inter = planet_inter.t1 - 0.001;',
            'vec3 scatter = out_scatter( offpos + dir * inter, -dir );',
            'vec4 atten = vec4( exp( -scatter ), 1.0 );',

            'gl_FragColor = 1.*atmos_sample( offpos, dir ) + ',
                'planet_color * atten;',
        '}'].join( '\n' );

    function Atmosphere( planet, base_camera ) {
        this.planet = planet;
        this.planet_scene = new THREE.Scene();
        this.planet_scene.add( planet.mesh );

        //this.planet_scene.add( new THREE.AmbientLight( 0x333333 ) );
        this.sun = new THREE.DirectionalLight( 0xffffff, 1 );
        this.sun.position.set( 0.707, 0.707, 0 );
        this.planet_scene.add( this.sun );

        this.planet_camera = new THREE.PerspectiveCamera(
            75., window.innerWidth / window.innerHeight, 1e3, 1e8 );
        base_camera.add( this.planet_camera );

        this.planet_texture = new THREE.WebGLRenderTarget(
            window.innerWidth, window.innerHeight, {
                minFilter: THREE.LinearFilter,
                magFilter: THREE.NearestFilter,
                format: THREE.RGBFormat 
            } );

        this.base_directions = [
            new THREE.Vector3( -1, 1, 0.5 ), new THREE.Vector3( 1, 1, 0.5 ),
            new THREE.Vector3( -1, -1, 0.5 ), new THREE.Vector3( 1, -1, 0.5 )];
        this.directions = [
            new THREE.Vector3( -1, 1, 0.5 ), new THREE.Vector3( 1, 1, 0.5 ),
            new THREE.Vector3( -1, -1, 0.5 ), new THREE.Vector3( 1, -1, 0.5 )];

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
	    var offset = new THREE.Vector3();
        for( var i = 0; i < 4; ++i ) {
            offset.setFromMatrixPosition( this.planet_camera.matrixWorld );
            this.directions[i].copy( this.base_directions[i] );
            this.directions[i].unproject( this.planet_camera );
            this.directions[i].sub( offset );
        }

        this.sun.position.set( Math.cos( Date.now() / 5000 ), 
            0, Math.sin( Date.now() / 5000 ) ).normalize();
        //this.sun.position.set( 0.9, 0., 0.1 ).normalize();

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

        this.attributes.sampleDir.needsUpdate = true;
        renderer.render( this.planet_scene, this.planet_camera,
            this.planet_texture, true );
        renderer.render( this.scene, this.camera );
    }
            
    return { SimplePlanet: SimplePlanet, Atmosphere: Atmosphere };
});
