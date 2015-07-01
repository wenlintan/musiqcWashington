

function Data( data, axes, options ) {
	this.options( {color: "black"} );
	if( options )	this.options( options );

	this.data = data;
	this.axes = axes;
	for( a in this.axes )
		this.axes[a].auto_scale( this.data[a] );
}

Data.prototype.options = function( options ) {
	if( options.color )		this.color = options.color;
}

Data.prototype.show = function ( ctx, plotdim ) {
	if( !this.data || !this.data[0].length || !this.data[1].length )
		return

	ctx.save();
	ctx.strokeStyle = this.color;
	ctx.translate( plotdim[0], plotdim[1] );
	var w = plotdim[2], h = plotdim[3];

	ctx.strokeStyle = this.color;
	ctx.lineWidth = this.width;
	ctx.beginPath();
	
	var xdata = this.data[0], ydata = this.data[1];
	var xaxis = this.axes[0], yaxis = this.axes[1];
	ctx.moveTo( xaxis.map(xdata[0])*w, yaxis.map(ydata[0])*h );
	for( pt in this.data[0] ) {
		var x = xaxis.map(xdata[pt]), y = yaxis.map(ydata[pt]);
		ctx.lineTo( x*w, y*h );
	}
	ctx.stroke();
	ctx.restore();
}

function Axis( options ) {
	this.options( {
		dimension: "x", label: "", label_color: "#000000",
		tick_labels: true, tick_label_color: "#000000",
		autoscale: true } );
	if( options )
		this.options( options );
}

Axis.prototype.options = function( options ) {
	if( options.dimension ) {
		this.dimension = options.dimension;
		this.calculate_dimensions();
	}
	
	if( options.label ) {
		this.label = options.label;
		this.calculate_dimensions();
	}
	if( options.label_color )	this.label_color = options.label_color;

	if( options.tick_labels ) {
		this.tick_labels = options.tick_labels;
		this.calculate_dimensions();
	}
	if( options.tick_label_color )	
		this.tick_label_color = options.tick_label_color;

	if( options.grid )			this.grid = options.grid;
	if( options.grid_color )	this.grid_color = options.grid_color;

	if( options.autoscale )		this.autoscale = options.autoscale;
	if( options.ticks ) {
		this.ticks = options.ticks;
		this.range = [ this.ticks[0], this.ticks[ this.ticks.length-1 ] ];
		this.autoscale = false;
	}
	if( options.range ) {
		this.range = options.range;
		this.ticks_from_range();
		this.autoscale = false;
	}
}

Axis.prototype.calculate_dimensions = function() {
	this.dimensions = [ 0, 0 ];
	var dim = 0;
	if( this.label )		dim += 20;
	if( this.tick_labels )	dim += 20;

	if( this.dimension == "y" )		this.dimensions[ 0 ] = dim;
	else							this.dimensions[ 1 ] = dim;
}

Axis.prototype.ticks_from_range = function () {
	this.ticks = [];
	var min = this.range[0];
	var r = this.range[1] - this.range[0];
	for( i=0; i<=10; i++ )
		this.ticks.push( min + r * i / 10. );
}	

Axis.prototype.auto_scale = function ( data ) {
	if( !this.autoscale || !data.length )
		return;
	
	var max = Math.max.apply( Math, data );
	var min = Math.min.apply( Math, data );

	if( this.range ) {
		max = Math.max( this.range[1], max );
		min = Math.min( this.range[0], min );
	}

	var range = max - min;
	if( range == 0. ) {
		min = min-1;
		max = max+1;
		range = max - min;
	}

	var rangepow = Math.floor( Math.log( range / 3. ) / Math.LN10 );
	this.display_decimal = 0;
	this.display_power = Math.round( rangepow / 3 ) * 3;
	if( this.display_power - rangepow > 0 )
		this.display_decimal = this.display_power - rangepow;

	rangepow = Math.pow( 10, rangepow );

	min = Math.floor( min / rangepow ) * rangepow;
	max = Math.ceil( max / rangepow ) * rangepow;
	this.range = [ min, max ];
	this.ticks_from_range();
}

Axis.prototype.map = function ( pt ) {
	var min = this.range[0], max = this.range[1];
	if(this.dimension == "y")	
		return 1. - (pt - min) / (max - min);
	return (pt - min) / (max - min );
}

Axis.prototype.claim = function( x, y, w, h ) {
	x += this.dimensions[ 0 ];
	w -= this.dimensions[ 0 ];
	h -= this.dimensions[ 1 ];
	return [x, y, w, h];
}

Axis.prototype.show = function ( ctx, plotdim ) {
	ctx.save();
	ctx.translate( plotdim[0], plotdim[1] + plotdim[3] );

	ctx.lineWidth = 1;
	ctx.strokeStyle = "#660000";
	ctx.font = "8pt Bold Times New Roman";

	if( this.dimension == "x" ) {
		var w = plotdim[ 2 ], h = this.dimensions[ 1 ];
	} else if( this.dimension == "y" ) {
		var w = plotdim[ 3 ], h = this.dimensions[ 0 ];
		ctx.translate( this.dimensions[1], -plotdim[3] );
		ctx.rotate( Math.PI / 2 );
	}

	ctx.moveTo( 0*w, 0.1*h );
	ctx.lineTo( 1.*w, 0.1*h );
	ctx.stroke();

	ticks = this.ticks;
	if( !ticks )	ticks = [-1., 1.];

	for( t in ticks ) {
		var tick = ticks[t];
		if( this.display_power )
			tick = tick / Math.pow( 10, this.display_power );

		text = tick.toFixed( this.display_decimal );
		suffix = {0: "", 3:"K", 6:"M", 9:"T"};
		neg_suffix = {9:"n", 6:"u", 3:"m"};
		if( this.display_power ) {
			if( this.display_power < 0 )
				text += neg_suffix[ -this.display_power ];
			else
				text += suffix[ this.display_power ];
		}

		x = t / (ticks.length - 1);
		if( this.dimension == "y" )
			x = 1. - x;
		
		// Draw tick mark
		ctx.moveTo( x*w, 0.1*h );
		ctx.lineTo( x*w, 0.*h );

		ctx.textAlign = "center";
		ctx.textBaseline = "top";
		ctx.fillStyle = "#000000";
		ctx.fillText( text, x*w, 0.2*h )
	}

	ctx.stroke();
	ctx.restore();	
}

function Plot() {
	this.x_axis = new Axis();
	this.y_axis = new Axis( {dimension: "y"} );
	this.axes = [ this.x_axis, this.y_axis ];

	this.data = [];
	this.width = this.height = 0;
}

Plot.prototype.plot = function( y, options ) {
	var xdata = [], i = 0;
	for( pt in y )
		xdata.push( i++ );
	var d = new Data( [xdata, y], [this.x_axis, this.y_axis], options );
	this.data.push( d );
}

Plot.prototype.reset = function( canvas ) {
	canvas.width = canvas.width;
}

Plot.prototype.resize = function( w, h ) {
	p = [10, 10, w-20, h-20];
	for( a in this.axes )
		p = this.axes[a].claim( p[0], p[1], p[2], p[3] );
	this.plot = p;
}

Plot.prototype.show = function( canvas ) {
	var width = canvas.width, height = canvas.height;
	if( !this.plot || width != this.width || height != this.height )
		this.resize( width, height );

	var ctx = canvas.getContext( '2d' );
	ctx.fillStyle = "#ffffff";
	ctx.fillRect( this.plot[0], this.plot[1], this.plot[2], this.plot[3] );
	ctx.strokeStyle = "#000000";
	ctx.strokeRect( this.plot[0], this.plot[1], this.plot[2], this.plot[3] );

	for( a in this.axes ) {
		this.axes[a].show( ctx, this.plot );
	}

	for( d in this.data ) {
		this.data[d].show( ctx, this.plot );
	}	
}


