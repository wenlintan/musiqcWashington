define(["particles"], function( particles ) {
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
        ctx.fillRect( 64-32, 0, 64+32, canvas.height );
		return canvas;
    }

    function Projectile( scene, world, position, worldmatrix, velocity ) {
        var extent = 0.5;
        this.dead = false;
		this.sprite = new THREE.Texture( generateTracerSprite() ); 
		this.sprite.needsUpdate = true;

        this.geometry = new THREE.BoxGeometry( 0.2, 0.2, extent );
        this.material = new THREE.MeshBasicMaterial( {
            map: this.sprite, transparent: true, color: 0xffaa00} );
        this.mesh = new THREE.Mesh( this.geometry, this.material );

        this.scene = scene;
        this.mesh.position.copy( position );
        this.mesh.quaternion.setFromRotationMatrix( worldmatrix );
        scene.add( this.mesh );

        var shape = new CANNON.Particle();
        this.body = new CANNON.Body({ mass: 0.01 });
        this.body.addShape( shape );

        this.world = world;
        this.body.position = position.clone();
        this.body.velocity = velocity.clone();
        world.add( this.body );

        var obj = this;
        this.body.addEventListener( "collide", function( ev ) {
            obj.onCollide( ev ); 
        });
    }

    Projectile.prototype.onCollide = function( event ) {
        console.log( "Damage!" );
    }

    Projectile.prototype.update = function() {
        this.mesh.position.copy( this.body.position );
        this.mesh.quaternion.copy( this.body.quaternion );
        if( Math.abs( this.mesh.position.x ) > 1000 ||
            Math.abs( this.mesh.position.y ) > 1000 ||
            Math.abs( this.mesh.position.z ) > 1000 ) {
            this.dead = true;    
            this.scene.remove( this.mesh );
            this.world.remove( this.body );
        }
    }

    function Weapon( scene, world, parent, position, direction ) {
        this.scene = scene;
        this.world = world;
        this.parent = parent;

        this.position = position;
        this.direction = direction;
        this.fireRate = 2;
        this.projectileSpeed = 10;

        this.firing = false;
        this.residual = 1;
        this.previousTime = Date.now();

		this.emitterObj = new THREE.Object3D();
		this.emitterObj.position.copy( position );
        //this.emitterObj.lookAt( direction );
		parent.mesh.add( this.emitterObj );

		this.emitterPos = new THREE.Vector3();
        this.emitterDir = new THREE.Vector3();
        this.projectiles = [];
    }

    Weapon.prototype.fire = function () {
        this.firing = true;
    }

    Weapon.prototype.update = function( world ) {
        this.projectiles.forEach( function(p) { p.update(); } );
        this.projectiles = this.projectiles.filter( function(p) { 
            return !p.dead; } );

        if( !this.firing ) {
            this.residual = 1;
            this.previousTime = Date.now();
            return;
        }

        this.firing = false;
		this.emitterPos.setFromMatrixPosition( this.emitterObj.matrixWorld );
        this.emitterDir.copy( this.direction );
        this.emitterDir.transformDirection( this.emitterObj.matrixWorld );

        var pos = new CANNON.Vec3(), vel = new CANNON.Vec3();
        pos.copy( this.emitterPos );
        pos.vadd( this.emitterDir, pos );

        this.emitterDir.multiplyScalar( this.projectileSpeed );
        vel.copy( this.emitterDir );
        vel.vadd( this.parent.body.velocity, vel );

        var delayTime = 1. / this.fireRate;
        var nparticles = (Date.now() - this.previousTime) / 1000. / delayTime;
        nparticles += this.residual;

        this.residual = nparticles - Math.floor( nparticles );
        nparticles = Math.floor( nparticles );
        for( var i = 0; i < nparticles; ++i ) {
            this.projectiles.push( new Projectile( 
                this.scene, this.world, pos, 
                this.emitterObj.matrixWorld, vel ) );
        }

        this.previousTime = Date.now();
    }

    return { Weapon: Weapon };
});

