define([], function() {
    function Level( filename, col_filename, scene, world ) {

        var obj = this;
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
            obj.body = new CANNON.Body({ mass: 0 });
            obj.body.addShape( shape );
            obj.body.quaternion.setFromAxisAngle( 
                new THREE.Vector3( 1, 0, 0 ), Math.PI/2 );
            world.add( obj.body );
            obj.loaded = true;
        }

        function callback( geometry, materials ) {

            var material = new THREE.MeshBasicMaterial({ color: 0xffff00 });
            obj.mesh = new THREE.Mesh( geometry, material );
            obj.mesh.rotateOnAxis( new THREE.Vector3( 1, 0, 0 ), Math.PI/2 );
            scene.add( obj.mesh );

            var loader = new THREE.JSONLoader();
            loader.load( col_filename, col_callback );

        }

        var loader = new THREE.JSONLoader();
        loader.load( filename, callback );
    }

    return { Level: Level };
});
