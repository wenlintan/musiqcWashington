require(['level', 'character'], function( Level, Character ) {
    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera( 
        75, window.innerWidth / window.innerHeight, 0.1, 1000 );
    camera.position.set( 0, 10, 10 );
    camera.lookAt( new THREE.Vector3( 0, 0, 0 ) );

    var renderer = new THREE.WebGLRenderer();
    renderer.setSize( window.innerWidth, window.innerHeight );
    renderer.autoClear = false;
    document.body.appendChild( renderer.domElement );

    var world = new CANNON.World();
    world.gravity.set(0, -10.0, 0);
    world.broadphase = new CANNON.NaiveBroadphase();
    world.solver.iterations = 10;

    var scene = new THREE.Scene();
    var current_level = new Level.Level( 
        'models/first_level.json', 'models/first_level.json', scene, world );
    var player = new Character.Character( 
        'models/cube.json', 'models/cube.json', scene, world );


    stats = new Stats();
    stats.domElement.style.position = 'absolute';
    stats.domElement.style.top = '0px';
    document.body.appendChild( stats.domElement );

    var lockElement = document.body;
    lockElement.requestPointerLock = 
        lockElement.requestPointerLock ||
        lockElement.mozRequestPointerLock ||
        lockElement.webkitRequestPointerLock;

    //Must be triggered from user input, otherwise will fail
    this.pointerLock = function() {
        lockElement.requestPointerLock();
    }
    
    var gui = new dat.GUI();
    gui.add( this, "pointerLock" );


    var render = function () {
        requestAnimationFrame(render);
        stats.update();

        world.step( 1. / 60 );

        player.update( 1. / 60 );
        renderer.render( scene, camera );
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

