define(function () {
    thrusterVertex = [
        'attribute vec3 velocity;',
        'attribute float birthTime;',
        'uniform float curTime;',

        'const vec4 startColor = vec4( 0.0, 0.0, 1.0, 1.0 );',
        'const vec4 endColor = vec4( 1.0, 0.7, 0.0, 0.0  );',

        'varying vec4 vColor;',
        'void main() {',
            'float t = curTime - birthTime;',
            'float ct = t * 3.0;',
            'vColor = startColor * (1.0 - ct) + endColor * ct;',
            'vec4 pos = vec4( position + velocity * t, 1.0 );',
            'gl_Position = projectionMatrix * modelViewMatrix * pos;',
            'gl_PointSize = 300. / gl_Position.z;',
        '}'
    ].join('\n');

    fragment = [
        'uniform sampler2D texture;',
        'varying vec4 vColor;',
        'void main() {',
            'vec4 tex = texture2D( texture, gl_PointCoord );',
            'gl_FragColor = tex * vColor;',
        '}'
    ].join('\n');

	function generateThrusterSprite() {
		var canvas = document.createElement( 'canvas' );
		canvas.width = 128;
		canvas.height = 128;
		
		var ctx = canvas.getContext( '2d' );
		ctx.beginPath();
		ctx.arc( canvas.width/2, canvas.height/2, canvas.width/2-2,
			0, Math.PI * 2, false );
		ctx.lineWidth = 0.5;
		ctx.stroke();
		ctx.restore();

		var gradient = ctx.createRadialGradient(
			canvas.width / 2, canvas.height / 2, 0,
			canvas.width / 2, canvas.height / 2, canvas.width / 2 );
		gradient.addColorStop( 0, 'rgba( 255, 255, 255, 1 )' );
		gradient.addColorStop( 0.2, 'rgba( 255, 255, 255, 1 )' );
		gradient.addColorStop( 0.4, 'rgba( 200, 200, 200, 0.6 )' );
		gradient.addColorStop( 1, 'rgba( 0, 0, 0, 0 )' );

		ctx.fillStyle = gradient;
		ctx.fill();
		return canvas;
	}

    tracerVertex = [
        'attribute vec3 velocity;',
        'attribute float birthTime;',
        'uniform float curTime;',

        'const vec4 startColor = vec4( 0.0, 0.0, 1.0, 1.0 );',
        'const vec4 endColor = vec4( 1.0, 0.7, 0.0, 0.0  );',

        'varying vec4 vColor;',
        'void main() {',
            'float t = curTime - birthTime;',
            'float ct = t * 3.0;',
            'vColor = startColor * (1.0 - ct) + endColor * ct;',
            'vec4 pos = vec4( position + velocity * t, 1.0 );',
            'gl_Position = projectionMatrix * modelViewMatrix * pos;',
            'gl_PointSize = 300. / gl_Position.z;',
        '}'
    ].join('\n');

    function generateTracerSprite() {
		var canvas = document.createElement( 'canvas' );
		canvas.width = 128;
		canvas.height = 128;
		
		var ctx = canvas.getContext( '2d' );
		var gradient = ctx.createLinearGradient(0, 0, canvas.width, 0);
		gradient.addColorStop( 0, 'rgba( 0, 0, 0, 0 )' );
        gradient.addColorStop( 0.5, 'rgba( 255, 255, 255, 255 )' );
		gradient.addColorStop( 1, 'rgba( 0, 0, 0, 0 )' );

		ctx.fillStyle = gradient;
        ctx.fillRect( 64-16, 0, 64+16, canvas.height );
		return canvas;
    }

    types = {
        thruster: { 
            vertex: thrusterVertex, 
            fragment: fragment, 
            sprite: generateThrusterSprite()
        },

        tracer: {
            vertex: tracerVertex,
            fragment: fragment,
            sprite: generateTracerSprite()
        }
    };

	function Pool( scene, nparticles, type ) {
		this.nparticles = nparticles;
		this.particles = new THREE.BufferGeometry({ dynamic: true });

        this.type = types[ type || "thruster" ];
		this.sprite = new THREE.Texture( this.type.sprite ); 
		this.sprite.needsUpdate = true;

        this.positions = new Float32Array( 3 * this.nparticles );
        this.velocities = new Float32Array( 3 * this.nparticles );
        this.birthTimes = new Float32Array( this.nparticles );

        this.startTime = Date.now();
		for( var i = 0; i < nparticles; ++i ) {
            this.birthTimes[ i ] = 0.0;
		}

		this.attributes = {
            velocity: { type: "v3", value: null },
            birthTime: { type: "f", value: null }
        };

		this.uniforms = { 
            curTime: {type: "f", value: 1.0},
            texture: {type: "t", value: this.sprite} 
        };

        this.particles.addAttribute( "position", 
            new THREE.BufferAttribute( this.positions, 3 ) );
        this.particles.addAttribute( "velocity",
            new THREE.BufferAttribute( this.velocities, 3 ) );
        this.particles.addAttribute( "birthTime",
            new THREE.BufferAttribute( this.birthTimes, 1 ) );

		this.material = new THREE.ShaderMaterial( {
			uniforms: this.uniforms,
			attributes: this.attributes,
			
			vertexShader: this.type.vertex,
			fragmentShader: this.type.fragment,
			
			blending: THREE.AdditiveBlending,
			depthWrite: false,
			transparent: true,
		} );

		this.cloud = new THREE.PointCloud( this.particles, this.material );
		scene.add( this.cloud );

        this.index = 0;
	}

	Pool.prototype.createParticle = function( pos, vel ) {
        this.positions[ 3*this.index ] = pos.x;
        this.positions[ 3*this.index +1 ] = pos.y;
        this.positions[ 3*this.index +2 ] = pos.z;

        this.velocities[ 3*this.index ] = vel.x;
        this.velocities[ 3*this.index +1 ] = vel.y;
        this.velocities[ 3*this.index +2 ] = vel.z;

        this.birthTimes[ this.index ] = (Date.now() - this.startTime) / 1000.;
        this.index = (this.index + 1) % this.nparticles;
	}

	Pool.prototype.update = function( id, pos, col ) {
        this.uniforms.curTime.value = (Date.now() - this.startTime) / 1000.;
        this.particles.attributes.position.needsUpdate = true;
        this.particles.attributes.velocity.needsUpdate = true;
        this.particles.attributes.birthTime.needsUpdate = true;
	}

    function Emitter( pool, spawnRate, position, velocity ) {
        this.pool = pool;
        this.spawnRate = spawnRate;
        this.residual = 0;
        this.previousTime = Date.now();

        this.position = position;
        this.velocity = velocity;
    }

    Emitter.prototype.update = function( callback ) {
        var delayTime = 1. / this.spawnRate;
        var nparticles = (Date.now() - this.previousTime) / 1000. / delayTime;
        nparticles += this.residual;

        this.residual = nparticles - Math.floor( nparticles );
        nparticles = Math.floor( nparticles );
        for( var i = 0; i < nparticles; ++i ) {
            if( callback ) callback( this.position, this.velocity );
            this.pool.createParticle( this.position, this.velocity );
        }

        this.previousTime = Date.now();
    }

    return { Pool: Pool, Emitter: Emitter };
});
