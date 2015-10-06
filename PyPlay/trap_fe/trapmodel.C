
#include <fstream>
#include <vector>
#include <cmath>

struct Point3f {
	float x, y, z;
	Point3f( float x_, float y_, float z_ ): x(x_), y(y_), z(z_)
	{}

};

Point3f operator+( const Point3f& lhs, const Point3f& rhs ) {
	return Point3f( lhs.x+rhs.x, lhs.y+rhs.y, lhs.z+rhs.z );
}

std::ostream& operator<<( std::ostream& os, const Point3f& rhs ) {
	os << rhs.x << " " << rhs.y << " " << rhs.z;
	return os;
}

typedef unsigned short ushort;
void push_box( std::vector< ushort >& indices,
	ushort off, ushort x_off, ushort y_off, ushort z_off,
	ushort r_y_off = 0 ) {

	if( !r_y_off )	r_y_off = y_off;
	
	indices.push_back( off+y_off );
	indices.push_back( off+y_off+x_off );
	indices.push_back( off+x_off );
	indices.push_back( off );

	indices.push_back( off+y_off+z_off );
	indices.push_back( off+y_off+x_off+z_off );
	indices.push_back( off+x_off+z_off );
	indices.push_back( off+z_off );
}

void push_tri( std::vector< ushort >& indices,
	ushort one, ushort two, ushort three ) {
	
	indices.push_back( one );
	indices.push_back( two );
	indices.push_back( three );
}

void push_bound( std::vector< ushort >& indices,
	ushort off, ushort x_off, ushort y_off, ushort z_off,
	bool bottom = true, bool top = true,
	bool left = false, bool right = false ) {

	indices.push_back( off+y_off );	
	indices.push_back( off+y_off+x_off );	
	indices.push_back( off+x_off );	

	indices.push_back( off+y_off );	
	indices.push_back( off+x_off );	
	indices.push_back( off );	
/*
	indices.push_back( off+y_off+z_off );	
	indices.push_back( off+y_off+x_off+z_off );	
	indices.push_back( off+x_off+z_off );	

	indices.push_back( off+y_off+z_off );	
	indices.push_back( off+x_off+z_off );	
	indices.push_back( off+z_off );	
*/
	indices.push_back( off+y_off+z_off );	
	indices.push_back( off+x_off+z_off );	
	indices.push_back( off+y_off+x_off+z_off );	

	indices.push_back( off+y_off+z_off );	
	indices.push_back( off+z_off );	
	indices.push_back( off+x_off+z_off );	

	if( bottom ) {
		indices.push_back( off+y_off );	
		indices.push_back( off+y_off+z_off );	
		indices.push_back( off+y_off+x_off+z_off );	

		indices.push_back( off+y_off );	
		indices.push_back( off+y_off+x_off+z_off );	
		indices.push_back( off+y_off+x_off );	
	}

	if( top ) {
		indices.push_back( off );	
		indices.push_back( off+x_off+z_off );	
		indices.push_back( off+z_off );	

		indices.push_back( off );	
		indices.push_back( off+x_off );	
		indices.push_back( off+x_off+z_off );	
	}

	if( left ) {
		indices.push_back( off+y_off );	
		indices.push_back( off );	
		indices.push_back( off+z_off );	

		indices.push_back( off+y_off );	
		indices.push_back( off+z_off );	
		indices.push_back( off+y_off+z_off );	
	}

	if( right ) {
		indices.push_back( off+y_off+x_off );	
		indices.push_back( off+z_off+x_off );	
		indices.push_back( off+x_off );	

		indices.push_back( off+y_off+x_off );	
		indices.push_back( off+y_off+z_off+x_off );	
		indices.push_back( off+z_off+x_off );	
	}
}

void make_hole( std::vector< Point3f >& model_pts,
	float xoff, float yoff1, float yoff2,
	float radius, float z, float theta_step ) {

	bool skip2 = yoff1 == yoff2;

	model_pts.push_back( Point3f( xoff - radius, 1., z ) );
	model_pts.push_back( Point3f( xoff - radius, yoff1, z ) );
	if(!skip2) model_pts.push_back( Point3f( xoff - radius, yoff2, z ) );
	model_pts.push_back( Point3f( xoff - radius, -1., z ) );
	for( float t = theta_step; t < 3.14159265-theta_step/2.;
		t += theta_step ) {
		float x = -radius * cos(t) + xoff;
		float y = radius * sin(t);

		model_pts.push_back( Point3f( x, 1., z ) );
		model_pts.push_back( Point3f( x, y + yoff1, z ) );	
		model_pts.push_back( Point3f( x, -y + yoff1, z ) );	
		if(!skip2) model_pts.push_back( Point3f( x, y + yoff2, z ) );	
		if(!skip2) model_pts.push_back( Point3f( x, -y + yoff2, z ) );	
		model_pts.push_back( Point3f( x, -1., z ) );	
	}
	model_pts.push_back( Point3f( xoff + radius, 1., z ) );
	model_pts.push_back( Point3f( xoff + radius, yoff1, z ) );
	if(!skip2) model_pts.push_back( Point3f( xoff + radius, yoff2, z ) );
	model_pts.push_back( Point3f( xoff + radius, -1., z ) );
}

int main( int argc, char** argv ) {
	unsigned short theta_res = 10;
	unsigned short z_res = 1;
	float needle_length = 0.75; //0.875;
	float needle1_height = 0.; //-.04;
	float needle2_height = 0.; //-.125;
	float needle_radius = 0.05;
	float radius = 0.125;

	float theta_step = 3.14159265 / theta_res;
	float z_step = 2. / z_res;

	std::vector< Point3f > model_pts;
	std::vector< unsigned short > conn;

	for( float z = -1; z < 1.+z_step/2; z += z_step ) {
		model_pts.push_back( Point3f( -1., 1., z ) );
		model_pts.push_back( Point3f( -1., 0.5, z ) );
		model_pts.push_back( Point3f( -1., -0.5, z ) );
		model_pts.push_back( Point3f( -1., -1., z ) );

		make_hole( model_pts, -.5, .5, -.5, radius, z, theta_step );
	
		float nr = 0., ny = 0.;
		if( z < -1. + needle_length ) {
			nr = needle_radius;// * (-z - 1. + needle_length);
			ny = needle1_height;
		} else if( z > 1. - needle_length ) {
			nr = needle_radius;// * (z - 1. + needle_length);
			ny = needle2_height;
		}

		if( nr ) 
			make_hole( model_pts, 0., ny, ny, nr, z, theta_step );


		make_hole( model_pts, .5, .5, -.5, radius, z, theta_step );

		model_pts.push_back( Point3f( 1., 1., z ) );
		model_pts.push_back( Point3f( 1., 0.5, z ) );
		model_pts.push_back( Point3f( 1., -0.5, z ) );
		model_pts.push_back( Point3f( 1., -1., z ) );
	}
	model_pts.push_back( Point3f( 0., needle1_height, -1. + needle_length ) );
	model_pts.push_back( Point3f( 0., needle2_height, 1. - needle_length ) );

	unsigned short off = 0, z_off = 30 + (2*6 + 4)*(theta_res-1); 
	//24 + 2*6*(theta_res-1);
	for( unsigned short z = 0; z < z_res; ++z ) {
	
		// Boxes up to start of rods
		push_bound( conn, off, 4, 1, z_off, false, true, true );
		push_bound( conn, off+1, 4, 1, z_off, false, false, true );
		push_bound( conn, off+2, 4, 1, z_off, true, false, true );
		off += 4;

		// First box along rods
		push_bound( conn, off, 4, 1, z_off );
		push_bound( conn, off+1, 5, 1, z_off );
		push_bound( conn, off+2, 6, 1, z_off );
		off += 4;

		for( unsigned short t = 1; t < theta_res-1; ++t ) {
			push_bound( conn, off, 6, 1, z_off );
			push_bound( conn, off+2, 6, 1, z_off ); 
			push_bound( conn, off+4, 6, 1, z_off ); 
			off += 6;
		}

		push_bound( conn, off, 6, 1, z_off );
		push_bound( conn, off+2, 5, 1, z_off );
		push_bound( conn, off+4, 4, 1, z_off );
		off += 6;

		//push_bound( conn, off, 4, 1, z_off, false, true );
		//push_bound( conn, off+1, 4, 1, z_off, false, false );
		//push_bound( conn, off+2, 4, 1, z_off, true, false );
		//off += 4;	

		// Start of needle stuff
		push_bound( conn, off, 4, 1, z_off, false, true );
		push_bound( conn, off+2, 3, 1, z_off, true, false );
		push_tri( conn, off+2, off+2+3, off+1 );
		push_tri( conn, off+2+z_off, off+1+z_off, off+2+3+z_off );
		off += 4;	

		// First box along rods
		size_t npts = model_pts.size();
		push_bound( conn, off, 3, 1, z_off, false, true );
		push_bound( conn, off+1, 4, 1, z_off, true, false );
		push_tri( conn, off+1, npts-2, off+1+3 );
		push_tri( conn, off+1, off+1+4, npts-2);
		push_tri( conn, off+1+z_off, off+1+3+z_off, npts-1 );
		push_tri( conn, off+1+z_off, npts-1, off+1+4+z_off );
		off += 3;

		for( unsigned short t = 1; t < theta_res-1; ++t ) {
			push_bound( conn, off, 4, 1, z_off, false, true );
			push_bound( conn, off+2, 4, 1, z_off, true, false ); 
			push_tri( conn, off+1, npts-2, off+1+4 );
			push_tri( conn, off+2, off+2+4, npts-2);
			push_tri( conn, off+1+z_off, off+1+4+z_off, npts-1 );
			push_tri( conn, off+2+z_off, npts-1, off+2+4+z_off );
			off += 4;
		}

		push_bound( conn, off, 4, 1, z_off, false, true );
		push_bound( conn, off+2, 3, 1, z_off, true, false );
		push_tri( conn, off+1, npts-2, off+1+4 );
		push_tri( conn, off+2, off+2+3, npts-2);
		push_tri( conn, off+1+z_off, off+1+4+z_off, npts-1 );
		push_tri( conn, off+2+z_off, npts-1, off+2+3+z_off );
		off += 4;

		push_bound( conn, off, 3, 1, z_off, false, true );
		push_bound( conn, off+1, 4, 1, z_off, true, false );
		push_tri( conn, off+1, off+1+4, off+1+3 );
		push_tri( conn, off+1+z_off, off+1+3+z_off, off+1+4+z_off );
		off += 3;	
		// End of needle stuff

		// First box along rods
		push_bound( conn, off, 4, 1, z_off );
		push_bound( conn, off+1, 5, 1, z_off );
		push_bound( conn, off+2, 6, 1, z_off );
		off += 4;

		for( unsigned short t = 1; t < theta_res-1; ++t ) {
			push_bound( conn, off, 6, 1, z_off );
			push_bound( conn, off+2, 6, 1, z_off ); 
			push_bound( conn, off+4, 6, 1, z_off ); 
			off += 6;
		}

		push_bound( conn, off, 6, 1, z_off );
		push_bound( conn, off+2, 5, 1, z_off );
		push_bound( conn, off+4, 4, 1, z_off );
		off += 6;

		push_bound( conn, off, 4, 1, z_off, false, true, false, true );
		push_bound( conn, off+1, 4, 1, z_off, false, false,false,true );
		push_bound( conn, off+2, 4, 1, z_off, true, false, false,true );
		off += 8;	
	}

	size_t pt_per_elem = 3, elem_type = 3;
	//size_t pt_per_elem = 8, elem_type = 10;

	std::ofstream f( "test.xda" );
	f << "DEAL 003:003" << std::endl;
	f << conn.size() / pt_per_elem << "\t# Num elements" << std::endl;
	f << model_pts.size() << "\t# Num nodes" << std::endl;
	f << conn.size() << "\t# Conn list length" << std::endl;
	f << 0 << "\t# Num boundary conditions" << std::endl;

	f << 65536 << "\t# String size" << std::endl;
	f << 1 << "\t# Num element blocks" << std::endl;
	f << elem_type << "\t# Element type in each block" << std::endl;
	f << conn.size() / pt_per_elem << "\t# Num elements in each block" << std::endl;

	f << "Id String" << std::endl;
	f << "Title String" << std::endl;

	for( size_t i = 0; i < conn.size(); i += pt_per_elem ) {
		for( size_t j = 0; j < pt_per_elem-1; ++j )		
			f << conn[i+j] << " ";
		f << conn[i+pt_per_elem-1] << std::endl;
	}

	for( size_t i = 0; i < model_pts.size(); ++i ) {
		f << model_pts[i] << std::endl;
	}
	f.close();

	std::ofstream tf( "test.ply" );
	tf << "ply" << std::endl;
	tf << "format ascii 1.0" << std::endl;
	tf << "element vertex " << model_pts.size() << std::endl;
	tf << "property float x" << std::endl;
	tf << "property float y" << std::endl;
	tf << "property float z" << std::endl;
	tf << "element face " << conn.size() / pt_per_elem << std::endl;
	tf << "property list uchar int vertex_index" << std::endl;
	tf << "end_header" << std::endl;

	for( size_t i = 0; i < model_pts.size(); ++i ) {
		tf << model_pts[i] << std::endl;
	}

	for( size_t i = 0; i < conn.size(); i += pt_per_elem ) {
		tf << "3 ";
		for( size_t j = 0; j < pt_per_elem-1; ++j )
			tf << conn[i+j] << " ";
		tf << conn[i+pt_per_elem-1] << std::endl;
	}
	tf.close();
	
	return 0;
}

/**/
