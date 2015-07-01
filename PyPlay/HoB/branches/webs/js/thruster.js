define(["particles"], function(particles) {

	function Thruster( pool, parent, body, maxforce, position, direction ) {
		this.pool = pool;
		this.parent = parent;
		this.body = body;

        this.position = position;
		this.direction = direction;
		this.maxForce = maxforce;
		this.throttle = 0;
        this.disabled = false;

		this.emitterObj = new THREE.Object3D();
		this.emitterObj.position.copy( position );
		parent.add( this.emitterObj );

		this.emitterPos = new THREE.Vector3();
        this.emitterPos.copy( position );
        this.emitterDir = new THREE.Vector3();
        this.emitter = new particles.Emitter( 
            pool, 10, this.emitterPos, this.emitterDir );
	}

	Thruster.prototype.setThrottle = function( t ) {
		t = Math.max( 0, Math.min( 100, t ) );
		this.throttle = t;
		this.emitter.spawnRate = t;
	}	

    Thruster.prototype.damage = function( dv ) {
        this.disabled = true;
    }

	Thruster.prototype.update = function () {	
        if( this.disabled ) return;

		this.emitterPos.setFromMatrixPosition( this.emitterObj.matrixWorld );
		var fpos = new CANNON.Vec3();
		fpos.copy( this.emitterPos );

        this.emitterDir.copy( this.direction );
        this.emitterDir.transformDirection( this.emitterObj.matrixWorld );
        this.emitterDir.multiplyScalar( 2. );
        this.emitterDir.negate();
        this.emitter.update();

		var force = new CANNON.Vec3();
		force.copy( this.emitterDir );
        force.scale( 1. / 2, force );
        force.negate( force );
		force.scale( this.maxForce * this.throttle / 100, force );

		this.body.applyForce( force, fpos );
	}

	return { Thruster: Thruster };
});
