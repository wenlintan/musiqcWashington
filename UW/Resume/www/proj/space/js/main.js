require(["planet"], function(planet) {
    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera( 
        75, window.innerWidth / window.innerHeight, 0.1, 1000 );
	var planet_camera = new THREE.PerspectiveCamera(
		75, window.innerWidth / window.innerHeight, 1e3, 1e8 );

    var renderer = new THREE.WebGLRenderer();
    renderer.setSize( window.innerWidth, window.innerHeight );
	renderer.autoClear = false;
    document.body.appendChild( renderer.domElement );

    var planet_scene = new THREE.Scene();
    var planet1 = new planet.SimplePlanet( planet_scene );
	var atmosphere = new planet.Atmosphere( planet1, camera );

    planet_scene.add( new THREE.AmbientLight( 0x333333 ) );
    var sun = new THREE.DirectionalLight( 0xffffff, 1 );
    sun.position.set( 5, 3, 5 );
    planet_scene.add( sun );

    var gui = new dat.GUI();
	gui.add( atmosphere, 'rayleigh_length' );
	gui.add( atmosphere, 'rayleigh_constant' );
	gui.add( atmosphere, 'mie_length' );
	gui.add( atmosphere, 'mie_constant' );

    stats = new Stats();
    stats.domElement.style.position = 'absolute';
    stats.domElement.style.top = '0px';
    document.body.appendChild( stats.domElement );

    var lockElement = document.body;
    lockElement.requestPointerLock = 
        lockElement.requestPointerLock ||
        lockElement.mozRequestPointerLock ||
        lockElement.webkitRequestPointerLock;

    this.pointerlock = function() {
        //Must be triggered from user input, otherwise will fail
        lockElement.requestPointerLock();
    }

    gui.add( this, 'pointerlock' ).name( "Click to lock mouse pointer." );
    
    camera.position.z = -1;
	camera.add( planet_camera );

    var render = function () {
        requestAnimationFrame(render);
        stats.update();

        var vel = new THREE.Vector3( 0, 0, 0 );
        var angvel = new THREE.Vector3( 0, 0, 0 );
        if( Keyboard.isDown( Keyboard.LEFT ) )    vel.x = 10;
        if( Keyboard.isDown( Keyboard.RIGHT ) )   vel.x = -10;
        if( Keyboard.isDown( Keyboard.UP ) )      vel.z = -10;
        if( Keyboard.isDown( Keyboard.DOWN ) )    vel.z = 10;

        if( Mouse.dx )                  angvel.y = Mouse.dx;
        if( Mouse.dy )                  angvel.x = Mouse.dy;
        Mouse.dx = Mouse.dy = 0;

		renderer.clear();
        atmosphere.render( renderer );
    };

    var Keyboard = {
        _pressed: {},
        F1: 112,
        TAB: 9,
        N1: 49,
		SHIFT: 16,

        SPACE: 32,
        LEFT: 37,
        UP: 38,
        RIGHT: 39,
        DOWN: 40,

        isDown: function ( keyCode ) {
            return this._pressed[ keyCode ];
        },

        onKeydown: function ( event ) {
            this._pressed[ event.keyCode ] = true;
        },

        onKeyup: function ( event ) {
            delete this._pressed[ event.keyCode ];
        }
    };

    window.addEventListener( 'keyup', function(event) {
        Keyboard.onKeyup(event); }, false ); 
    window.addEventListener( 'keydown', function(event) {
        Keyboard.onKeydown(event); }, false );

    var Mouse = {
        dx: 0,
        dy: 0,
        buttons: {}
    };
    
    function onPointerLockChange( event ) {
        document.pointerLockElement = document.pointerLockElement ||
            document.mozPointerLockElement || document.webkitPointerLockElement;
        if( document.pointerLockElement === lockElement ) {
            document.addEventListener( 'mousemove', onMouseMove, false );
        } else {
            document.removeEventListener( 'mousemove', onMouseMove, false );
            Mouse.dx = Mouse.dy = 0;
            Mouse.buttons = {};
        }
    }

    function onMouseMove( event ) {
        Mouse.dx = event.movementX || event.mozMovementX || 
            event.webkitMovementX || 0;
        Mouse.dy = event.movementY || event.mozMovementY || 
            event.webkitMovementY || 0;
    }
    document.addEventListener( 'pointerlockchange', 
        onPointerLockChange, false );
    document.addEventListener( 'mozpointerlockchange', 
        onPointerLockChange, false );
    document.addEventListener( 'webkitpointerlockchange', 
        onPointerLockChange, false );

    window.addEventListener( 'mousedown', function( event ) {
        Mouse.buttons[ event.button ] = true;
    } );
    window.addEventListener( 'mouseup', function( event ) {
        Mouse.buttons[ event.button ] = false;
    } );

    function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix()
        renderer.setSize( window.innerWidth, window.innerHeight );
    }
    window.addEventListener( 'resize', onWindowResize );
        
    render();
})

