
last = 0
loading = false
function load_recent_data( data ) {
	loading = true;
	var req = new XMLHttpRequest();
	req.open("GET", "http://" + location.host + "/recent?l=" + last, true);
	req.onreadystatechange = function() {
		if( req.readyState == 4 && (req.status == 200 || req.status == 0) ) {
			document.getElementById("log").innerHTML = req.responseText;
			vals = JSON.parse( req.responseText );

			if( "out" in vals ) {
				for( l in vals["out"] ) for( o in vals["out"][l] ) {
					if( data[o].length > 5000 )		data[o].shift();
					data[o].push( vals["out"][l][o] );
				}
			}
			
			if( "l" in vals )
				last = vals["l"];
			if( "params" in vals )
				parameters( false, 0 );
			
			loading = false;
		}
	}
	req.send();
}

function tick( canvas, ctx, data ) {
	if( !loading )
		load_recent_data( data );
		
	var plot_data = new Array();
	
	var plots = ["first", "second", "third"];
	var colors = ["#0000FF", "#00FF00","#FF0000"];
	for( i = 0; i < plots.length; ++i ) {
		elem = document.getElementById( plots[i] );
		elem.style.background = colors[i];
		
		if( elem.checked )		plot_data.push( data[i] );
		else					plot_data.push( [] );
	}
	
	draw_graph(canvas, ctx, plot_data, colors);
}

function set_callback( i ) {
	var sub = document.getElementById("S" + i);
	sub.onclick = function() {	parameters( true, i );	}
}

function start() {	
	var canvas = document.getElementById("plox2");
	var ctx = canvas.getContext("2d");
  
	for( i = 0; i < 3; ++i ) 
		set_callback(i);
	
	var legend = document.getElementById("legend");
	legend.style.top = canvas["offsetTop"];
	legend.style.left = canvas.width - legend.style.width;
  
	parameters( false, 0 );
	var data = [ new Array(), new Array(), new Array() ];
	window.setInterval( function(){ tick(canvas, ctx, data); }, 1000 );
}
