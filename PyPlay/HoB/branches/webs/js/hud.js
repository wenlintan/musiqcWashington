define(function() {
    function HUD( parent ) {
        this.parent = parent;

        this.canvas = document.createElement( "canvas" );
        this.canvas.style.position = "absolute";
        this.canvas.style.bottom = "0px";
        this.canvas.width = 200;
        this.canvas.height = 200;

        document.body.appendChild( this.canvas );
    }

    HUD.prototype.drawThruster = function(ctx, thruster) {
        if( !thruster ) return;
        var r = 0, g = 0,  b = 0;
        if( thruster.disabled ) {
            r = 255;
        } else {
            g = 200;
            b = Math.floor( 200 - thruster.throttle * 2 );
            r = Math.floor( 200 - thruster.throttle * 2 );
        }

        ctx.beginPath();
        ctx.strokeStyle = 'rgb(' + r + ',' + g + ',' + b + ')';
        ctx.moveTo( 10, 0 );
        ctx.quadraticCurveTo( 30, 10, 30, 15 );
        ctx.lineTo( 30, 85 );
        ctx.quadraticCurveTo( 30, 90, 10, 100 );
        ctx.quadraticCurveTo( 50, 90, 50, 85 );
        ctx.lineTo( 50, 15 );
        ctx.quadraticCurveTo( 50, 10, 10, 0 );

        for( var y = -1; y < 2; ++y ) {
            ctx.moveTo( 0, 20 * y + 50 );
            ctx.lineTo( 25, 20 * y + 50 );
        }
        ctx.stroke();
    }


    HUD.prototype.update = function() {
        //return;
		var ctx = this.canvas.getContext( '2d' );
        ctx.strokeStyle = '#ff0000';

        ctx.setTransform( 0, -0.2, 0.2, 0, 35, 60 );
        this.drawThruster( ctx, this.parent.thrusters[0].thruster );
        ctx.setTransform( 0, 0.2, 0.2, 0, 35, 0 );
        this.drawThruster( ctx, this.parent.thrusters[1].thruster );

        ctx.setTransform( 0.2, 0, 0, 0.2, 10, 0 );
        this.drawThruster( ctx, this.parent.thrusters[2].thruster );
        ctx.setTransform( -0.2, 0, 0, 0.2, 80, 0 );
        this.drawThruster( ctx, this.parent.thrusters[3].thruster );

        ctx.setTransform( 0.2, 0, 0, 0.2, 10, 40 );
        this.drawThruster( ctx, this.parent.thrusters[4].thruster );
        ctx.setTransform( -0.2, 0, 0, 0.2, 80, 40 );
        this.drawThruster( ctx, this.parent.thrusters[5].thruster );

    }

    return { HUD: HUD };
});
