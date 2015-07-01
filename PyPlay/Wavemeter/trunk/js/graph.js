
function draw_graph( canvas, ctx, pt_lists, options ) {
	var colors = 'colors' in options? options.colors : ['black'];
	var axes = 'axes' in options? options.axes : true;
	var grid = 'grid' in options? options.grid : true;
	var labels = 'labels' in options? options.labels :true;
	
	if( pt_lists.length == 0 )
		return;
		
	canvas.width = canvas.width; // reset canvas
	
	//offset x and y-axes if we need to draw labels
	if( labels ) {
		var xaxis = 100, yaxis = 50;
	} else {
		var xaxis = 0, yaxis = 0;
	}
	
	var width = canvas.width, height = canvas.height;
	var grid_width = width - xaxis, grid_height = height - yaxis;
	
	ctx.lineWidth = 1;
	ctx.strokeStyle = "#000000";
	ctx.strokeRect( xaxis + 1, 1, width - xaxis - 2, height - yaxis - 2 );
	
	var xmin = 0;
	var xmax = Math.max.apply( Math, pt_lists.map( function(i){ return i.length - 1; } ) );
	var ymax = Math.max.apply( Math, pt_lists.map( function(i){ return Math.max.apply( Math, i ); } ) );
	var ymin = Math.min.apply( Math, pt_lists.map( function(i){ return Math.min.apply( Math, i ); } ) );
	
	//if( xrange / xmin > 1000 ) ;
	//xrangepow = Math.floor( Math.ln( xrange ) * Math.LN10 );
	//xrange = Math.ciel( xrange / Math.pow( 10, xrangepow ) ) * Math.pow( 10, xrangepow );
	
	var xrange = (xmax - xmin), yrange = (ymax - ymin) * 1.1;
	if( yrange == 0 )	yrange = 100;
	ymin = ymin - yrange * 0.05;
	
	var xscale = (canvas.width - xaxis) / xrange, xoff = xmin - xaxis / xscale;
	var yscale = -(canvas.height - yaxis) / yrange, yoff = ymin - (height - yaxis) / yscale;
	
	// draw axes
	ctx.lineWidth = 1;
	ctx.strokeStyle = "#000000";
	
	if( axes ) {
		ctx.beginPath();
		ctx.moveTo( (0 - xoff) * xscale, 0 );
		ctx.lineTo( (0 - xoff) * xscale, canvas.height - yaxis );
		ctx.moveTo( xaxis, (0 - yoff) * yscale );
		ctx.lineTo( canvas.width, (0 - yoff) * yscale );
		ctx.stroke();
	}
	
	// draw grid and labels
	ctx.lineWidth = 0.1;
	ctx.strokeStyle = "#666666";
	ctx.font = "Bold Times New Roman 18pt";
	
	if( grid || labels ) {
		ctx.beginPath();
		for( i = 0; i < 10; ++i ) {
			if( grid ) {
				ctx.moveTo( xaxis + i / 10 * grid_width, grid_height );
				ctx.lineTo( xaxis + i / 10 * grid_width, 0 );
				
				ctx.moveTo( xaxis, grid_height - i / 10 * grid_height );
				ctx.lineTo( width, grid_height - i / 10 * grid_height );
			}
			
			if( labels ) {
				ctx.textAlign = "center";
				ctx.textBaseline = "top";
				var text = (xmin + i / 10 * xrange).toFixed(0)
				ctx.fillText( text, xaxis + i / 10 * grid_width, grid_height+2, grid_width / 15 )
				
				ctx.textAlign = 'right';
				ctx.textBaseline = 'middle';
				var text = (ymin + i / 10 * yrange).toFixed(0)
				ctx.fillText( text, xaxis-2, grid_height - i / 10 * grid_height, xaxis );
			}
		}
		ctx.stroke();
	}
	
	for( list in pt_lists ) {
		if( pt_lists[list].length < 2 )
			continue;
			
		ctx.strokeStyle = colors[ parseInt(list) % colors.length ];
		ctx.lineWidth = 1;
		ctx.beginPath();
		
		ctx.moveTo( xaxis, ( pt_lists[list][0] - yoff ) * yscale );
		for( pt in pt_lists[list] ) {
			var x = ( pt - xoff ) * xscale;
			var y = ( pt_lists[list][pt] - yoff ) * yscale;
			ctx.lineTo( x, y );
		}
		ctx.stroke();
	}
}
