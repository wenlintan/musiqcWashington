define([], function() {
    function Character( filename, col_filename, scene, world ) {

        var obj = this;
        this.loaded = false;
        function col_callback( geometry, materials ) {
            var shape = new CANNON.ConvexPolyhedron( 
                geometry.vertices.map( function( vec ) {
                    var cvec = new CANNON.Vec3();
                    cvec.copy( vec );
                    return cvec;
                }), 
                geometry.faces.map( function( face ) {
                    return [face.a, face.b, face.c];
                }) );
            obj.body = new CANNON.Body({ mass: 1 });
            obj.body.addShape( shape );
            obj.body.quaternion.setFromAxisAngle( 
                new THREE.Vector3( 1, 0, 0 ), Math.PI/2 );
            obj.body.position.set( 1, 10, 0 );
            world.add( obj.body );
            obj.loaded = true;
        }

        function callback( geometry, materials ) {

            var material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
            obj.mesh = new THREE.Mesh( geometry, material );
            obj.mesh.rotateOnAxis( new THREE.Vector3( 1, 0, 0 ), Math.PI/2 );
            obj.mesh.position.set( 1, 3, 0 );
            scene.add( obj.mesh );

            var loader = new THREE.JSONLoader();
            loader.load( col_filename, col_callback );

        }

        var loader = new THREE.JSONLoader();
        loader.load( filename, callback );
    }

    Character.prototype.update = function( dt ) {
        if( !this.loaded ) return;
        this.mesh.position.copy( this.body.position );
        this.mesh.quaternion.copy( this.body.quaternion );
    }

    function FSM( start ) {

    }

    return { Character: Character };

});
