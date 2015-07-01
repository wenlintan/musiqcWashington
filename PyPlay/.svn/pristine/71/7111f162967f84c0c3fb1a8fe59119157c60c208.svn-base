define(["thruster", "particles", "weapon"], 
function( thruster, particles, weapon ) {
	
	function PIDController( nchannels, P, I, D ) {
		this.nchannels = nchannels;
		this.P = P;		this.I = I;		this.D = D;

		this.outputs = []
		this.previous = []
		this.integrals = []
		for( var i = 0; i < nchannels; ++i ) {
			this.outputs.push( 0 );
			this.previous.push( 0 );
			this.integrals.push( 0 );
		}
	}

	PIDController.prototype.update = function ( errors ) {
		var obj = this;
		errors.forEach( function( error, index ) { 
			obj.outputs[ index ] = obj.P * error +
				obj.I * obj.integrals[ index ] +
				obj.D * (error - obj.previous[ index ] );
			obj.previous[ index ] = error;
			obj.integrals[ index ] += error;
		} )
	}


	function Ship( scene, world, modelname, components ) {
		this.thrusters = components && components.thrusters?
            components.thrusters : [
			{	position: new THREE.Vector3( 0, 0, 1 ),
				direction: new THREE.Vector3( 0, 0, -1 ),
				maxThrust: 4.2 },
			{	position: new THREE.Vector3( 0, 0, -1 ),
				direction: new THREE.Vector3( 0, 0, 1 ),
				maxThrust: 1.5 },
			{	position: new THREE.Vector3( 1, 0, 0.5 ),
				direction: new THREE.Vector3( -1, 0, 0 ),
				maxThrust: 1.5 },
			{	position: new THREE.Vector3( -1, 0, 0.5 ),
				direction: new THREE.Vector3( 1, 0, 0 ),
				maxThrust: 1.5 },
			{	position: new THREE.Vector3( 1, 0, -0.5 ),
				direction: new THREE.Vector3( -1, 0, 0 ),
				maxThrust: 1.5 },
			{	position: new THREE.Vector3( -1, 0, -0.5 ),
				direction: new THREE.Vector3( 1, 0, 0 ),
				maxThrust: 1.5 },
			{	position: new THREE.Vector3( -0.5, 1, 0.5 ),
				direction: new THREE.Vector3( -0., -1, 0 ),
				maxThrust: 1.5 },
			{	position: new THREE.Vector3( -0.5, -1, 0.5 ),
				direction: new THREE.Vector3( -0., 1, 0 ),
				maxThrust: 1.5 },
			{	position: new THREE.Vector3( -0.5, 1, -0.5 ),
				direction: new THREE.Vector3( -0., -1, 0 ),
				maxThrust: 1.5 },
			{	position: new THREE.Vector3( -0.5, -1, -0.5 ),
				direction: new THREE.Vector3( -0., 1, 0 ),
				maxThrust: 1.5 },
			{	position: new THREE.Vector3( 0.5, 1, 0.5 ),
				direction: new THREE.Vector3( 0., -1, 0 ),
				maxThrust: 1.5 },
			{	position: new THREE.Vector3( 0.5, -1, 0.5 ),
				direction: new THREE.Vector3( 0., 1, 0 ),
				maxThrust: 1.5 },
			{	position: new THREE.Vector3( 0.5, 1, -0.5 ),
				direction: new THREE.Vector3( 0., -1, 0 ),
				maxThrust: 1.5 },
			{	position: new THREE.Vector3( 0.5, -1, -0.5 ),
				direction: new THREE.Vector3( 0., 1, 0 ),
				maxThrust: 1.5 } ];
			
        this.ai_controller = new PIDController( 6, 1, 0.0001, 0.2 );
		this.controller = new PIDController( 6, 10, 0.0001, 10 );

        this.world = world;

		var obj = this;
		this.loaded = false;
		function callback( geometry, materials ) {
			var material = new THREE.MeshBasicMaterial({ color: 0xffff00 });
			obj.mesh = new THREE.Mesh( geometry, material );
			scene.add( obj.mesh );

			var shape = new CANNON.Box( new CANNON.Vec3( 1, 1, 1 ) );
			obj.body = new CANNON.Body({ mass: 1 });
			obj.body.addShape( shape );
            obj.body.addEventListener( "collide", function( ev ) { 
                obj.collisionResponse( ev ); } );

            if( components && components.position ) 
                obj.body.position.copy( components.position );
            if( components && components.attach )
                obj.mesh.add( components.attach );

			world.add( obj.body );

			obj.pool = new particles.Pool( scene, 5000, "thruster" );
			for( var i = 0; i < obj.thrusters.length; ++i ) {
				obj.thrusters[i].thruster  = new thruster.Thruster( 
					obj.pool, obj.mesh, obj.body, obj.thrusters[i].maxThrust,
					obj.thrusters[i].position, obj.thrusters[i].direction );
			}

            obj.weapon = new weapon.Weapon( scene, world, obj,
                new THREE.Vector3( 0, 0, -1 ), new THREE.Vector3( 0, 0, -1 ) );

			obj.loaded = true;
		}

		var loader = new THREE.JSONLoader();
		loader.load( "models/cube.json", callback );
	}

    Ship.prototype.collisionResponse = function( event ) {
        dv = this.body.velocity.vsub( event.body.velocity ).norm();
        vec = event.contact.bi === this? event.contact.ri: event.contact.rj;
        vec = this.body.quaternion.conjugate().vmult( vec );

        for( var i = 0; i < this.thrusters.length; ++i ) {
            if( vec.vsub( this.thrusters[i].position ).norm() < 0.1 )
                this.thrusters[i].thruster.damage( dv );
        }

        //if( vec.vsub( this.weapon.position ).norm() < 0.1 )
            //this.weapon.damage( dv );
    }

	Ship.prototype.updateThrusters = function( 
		desired_velocity, desired_angular_velocity, update_vel ) {
		if( !this.loaded ) return;

		var velerror = desired_velocity.sub( 
            this.body.quaternion.conjugate().vmult( this.body.velocity ) );
		var angvelerror = desired_angular_velocity.sub(
            this.body.quaternion.conjugate().vmult( 
                this.body.angularVelocity ) );

		var errors = velerror.toArray();
		angvelerror.toArray().forEach( function(v) { errors.push(v); } )
		this.controller.update( errors );
		
		var outs = this.controller.outputs;
		var force = new THREE.Vector3( outs[0], outs[1], outs[2] );
		var torque = new THREE.Vector3( outs[3], outs[4], outs[5] );

        for( var i = 0; i < this.thrusters.length; ++i )
            this.thrusters[i].thruster.setThrottle( 0 );

		var cross = new THREE.Vector3(), scale = new THREE.Vector3();
        for( var iter = 0; iter < 5; ++iter ) 
		for( var i = 0; i < this.thrusters.length; ++i ) {
            if( this.thrusters[i].thruster.disabled ) continue;

			var dp = update_vel? force.dot( this.thrusters[i].direction ): 0;
            cross.crossVectors( this.thrusters[i].position,
                this.thrusters[i].direction );
            dp += torque.dot( cross );

            var oldthrottle = this.thrusters[i].thruster.throttle;
			var throttle = oldthrottle + 
                100 * dp / this.thrusters[i].maxThrust;
			throttle = Math.min( 100, Math.max( 0, throttle ) );

			scale.copy( this.thrusters[i].direction ).
				multiplyScalar( this.thrusters[i].maxThrust * 
                    (throttle - oldthrottle) / 100 );
			force.sub( scale );

            cross.multiplyScalar( this.thrusters[i].maxThrust *
                (throttle - oldthrottle) / 100 );
            torque.sub( cross );

			this.thrusters[i].thruster.setThrottle( throttle );
		}
	}

    Ship.prototype.alignTo = function( target ) {
        if( !this.loaded ) return;

        var dir = target.body? 
            this.body.quaternion.conjugate().vmult( 
                this.body.position.vsub( target.body.position ) ):
            target;
        dir.normalize();

        var rotx = Math.atan2( -dir.y, dir.z );
        var roty = Math.atan2( dir.x, dir.z );

        var errors = [0, 0, 0];
        var roterror = [rotx, roty, 0];
        roterror.forEach( function(v) { errors.push( v ); } )
        this.ai_controller.update( errors );

		var outs = this.ai_controller.outputs;
		var vel = new THREE.Vector3( outs[0], outs[1], outs[2] );
		var angvel = new THREE.Vector3( outs[3], outs[4], outs[5] );
        this.updateThrusters( vel, angvel );
    }

    Ship.prototype.fire = function() {
        this.weapon.fire();
    }

	Ship.prototype.update = function() {
		if( !this.loaded ) return;
		this.mesh.position.copy( this.body.position );
		this.mesh.quaternion.copy( this.body.quaternion );

		for( var i = 0; i < this.thrusters.length; ++i ) {
			this.thrusters[i].thruster.update();
		}
        this.pool.update();
        this.weapon.update();
	}
	
	return { Ship: Ship };
});

