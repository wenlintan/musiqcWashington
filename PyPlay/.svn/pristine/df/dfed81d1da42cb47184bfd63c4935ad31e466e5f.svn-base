
#include "geometry.h"

bool Geometry::initialize( const string& filename, shared_ptr<Renderer> rend ) {
	set_renderer( rend );
	return load_model( filename );
}

void Geometry::set_renderer( shared_ptr<Renderer> rend ) {
	_Renderer = rend;
}

void Geometry::create_plane( Vector3f& p1, Vector3f& p2, Vector3f& p3, Vector3f& p4 ) {
	Vertices.resize(0);
	Vertices.push_back( Vertex(p1) );
	Vertices.push_back( Vertex(p2) );
	Vertices.push_back( Vertex(p3) );
	Vertices.push_back( Vertex(p4) );

	Indices.resize(0);
	Indices.push_back( 0 ); Indices.push_back( 1 ); Indices.push_back( 3 );
	Indices.push_back( 1 ); Indices.push_back( 2 ); Indices.push_back( 3 );

	generate_normals();
}

void Geometry::create_cube( float w, float h, float d ) {
	Vertices.resize(0);
	Vertices.push_back( Vertex( Vector3f(-w/2,  h/2, -d/2) ) );
	Vertices.push_back( Vertex( Vector3f( w/2,  h/2, -d/2) ) );
	Vertices.push_back( Vertex( Vector3f( w/2, -h/2, -d/2) ) );
	Vertices.push_back( Vertex( Vector3f(-w/2, -h/2, -d/2) ) );
	Vertices.push_back( Vertex( Vector3f(-w/2,  h/2,  d/2) ) );
	Vertices.push_back( Vertex( Vector3f( w/2,  h/2,  d/2) ) );
	Vertices.push_back( Vertex( Vector3f( w/2, -h/2,  d/2) ) );
	Vertices.push_back( Vertex( Vector3f(-w/2, -h/2,  d/2) ) );

	Indices.resize(0);
	Indices.push_back( 0 ); Indices.push_back( 3 ); Indices.push_back( 1 );		//front
	Indices.push_back( 3 ); Indices.push_back( 2 ); Indices.push_back( 1 );

	Indices.push_back( 1 ); Indices.push_back( 2 ); Indices.push_back( 5 );		//right
	Indices.push_back( 2 ); Indices.push_back( 6 ); Indices.push_back( 5 );

	Indices.push_back( 5 ); Indices.push_back( 6 ); Indices.push_back( 4 );		//back
	Indices.push_back( 6 ); Indices.push_back( 7 ); Indices.push_back( 4 );

	Indices.push_back( 4 ); Indices.push_back( 7 ); Indices.push_back( 0 );		//left
	Indices.push_back( 7 ); Indices.push_back( 1 ); Indices.push_back( 0 );

	Indices.push_back( 0 ); Indices.push_back( 1 ); Indices.push_back( 4 );		//top
	Indices.push_back( 1 ); Indices.push_back( 5 ); Indices.push_back( 4 );

	Indices.push_back( 3 ); Indices.push_back( 7 ); Indices.push_back( 2 );		//bottom
	Indices.push_back( 2 ); Indices.push_back( 7 ); Indices.push_back( 6 );

	generate_normals();
}

void Geometry::create_tetrahedra(float h) {
	Vertices.resize(0);
	Vertices.push_back( Vertex( Vector3f( 0,   h,   0) ) );
	Vertices.push_back( Vertex( Vector3f(-h/2, 0,  -h/3) ) );
	Vertices.push_back( Vertex( Vector3f( h/2, 0,  -h/3) ) );
	Vertices.push_back( Vertex( Vector3f( 0,   0, 2*h/3) ) );

	Indices.resize(0);
	Indices.push_back( 0 ); Indices.push_back( 1 ); Indices.push_back( 2 );
	Indices.push_back( 0 ); Indices.push_back( 2 ); Indices.push_back( 3 );
	Indices.push_back( 0 ); Indices.push_back( 3 ); Indices.push_back( 1 );
	Indices.push_back( 2 ); Indices.push_back( 1 ); Indices.push_back( 3 );

	generate_normals();
}

void Geometry::create_cone(float radius, float h, uint tesselation) {
	Vertices.resize(0);
	Vertices.push_back( Vertex( Vector3f(0, h, 0) ) );
	for( uint i = 0; i < tesselation; ++i ) 
		Vertices.push_back( Vertex( Vector3f( (float)(radius*cos(i*2*G_PI/tesselation)), 0, 
											  (float)(radius*sin(i*2*G_PI/tesselation)) ) ) );
	Vertices.push_back( Vertex( Vector3f(0, 0, 0) ) );

	Indices.resize(0);
	for( uint i = 1; i < tesselation; ++i ) {
		Indices.push_back( 0 ); Indices.push_back( i ); Indices.push_back( i+1 );
	}
	Indices.push_back( 0 ); Indices.push_back( tesselation ); Indices.push_back( 1 );

	for( uint i = 1; i < tesselation; ++i ) {
		Indices.push_back( tesselation+1 ); Indices.push_back( i+1 ); Indices.push_back( i );
	}
	Indices.push_back( tesselation+1 ); Indices.push_back( 1 ); Indices.push_back( tesselation );
	generate_normals();

}

bool Geometry::load_model( const string& filename ) {

	Vertices.resize( 0 );
	Indices.resize( 0 );

	ifstream file( filename.c_str(), ifstream::in );
	if( !file.is_open() )
		return false;

	char buffer[1024];
	stringstream datatypes;

	string section, val;
	bool read_normals = false, read_rgb = false, read_uv = false;

	uint num_textures = 0, num_polys = 0, num_verts = 0;
	int texture = -1;

	Vector2f uv;
	Vector3f xyz, rgb, n;

	file >> section;
	file >> num_textures;

	for( uint i = 0; i < num_textures; ++i ) {
		file >> val;
		while( !val.length() ) file >> val;
	}

	file >> section;
	file >> num_polys;
	for( uint i = 0; i < num_polys; ++i ) {
		read_normals = read_rgb = read_uv = false;

		file >> num_verts;
		file >> texture;

		datatypes.clear();
		file.getline( buffer, 1024 );
		datatypes.str( string(buffer) );

		while( !datatypes.eof() ) {
			datatypes.getline( buffer, 1024, ' ' );
			if( string(buffer) == "NORMALS" )		read_normals = true;
			else if( string(buffer) == "RGB" )		read_rgb = true;
			else if( string(buffer) == "UV" )		read_uv = true;
			else if( string(buffer).size() )		
				LOG_ERR( buffer );

		}

		for( uint j = 0; j < num_verts; ++j ) {
			file >> xyz;
			if( read_normals)	file >> n;
			if( read_rgb )		file >> rgb;
			if( read_uv )		file >> uv;

			Vertices.push_back( Vertex( xyz, uv, n ) );

		}

	}

	if( !read_normals )	generate_normals();
	return true;
}

void Geometry::generate_normals() {

	for( size_t i = 0; i < Indices.size() || i < Vertices.size(); i+=3 ) {
		const Vector3f& p1 = Vertices[ Indices.size()?Indices[i]:i ].Coordinates, 
						p2 = Vertices[ Indices.size()?Indices[i+1]:i+1 ].Coordinates,
						p3 = Vertices[ Indices.size()?Indices[i+2]:i+2 ].Coordinates;

		Vector3f u = p2 - p1, v = p3 - p1;
		Vector3f n = u.cross_product( v ).normalize();

		Vertices[ Indices.size()?Indices[i]:i ].Normal += n;
		Vertices[ Indices.size()?Indices[i+1]:i+1 ].Normal += n;
		Vertices[ Indices.size()?Indices[i+2]:i+2 ].Normal += n;
	}

	for( size_t i = 0; i < Vertices.size(); ++i )
		Vertices[ i ].Normal.make_normalized();
}

vector<float> Geometry::build_collision_data( ushort res, ushort coll_per_step ) {

	if( !Vertices.size() )
		return vector<float>();

	vector<float>	result;

	float max_dist_sq = Vertices[0].Coordinates.length_sq();
	for( size_t i = 1; i < Vertices.size(); ++i )
		max_dist_sq = std::max( Vertices[i].Coordinates.length_sq(), max_dist_sq );

	float rho = max_dist_sq, delta = 2 * (float)G_PI / res;
	for( float theta = 0.0; theta < 2 * G_PI; theta += delta ) {
		for( float phi = 0.0; phi < 2 * G_PI; phi += delta ) {

			Vector3f start( rho*cosf(theta)*sinf(phi), rho*sinf(theta)*sinf(phi), rho*cosf(phi) );
			start += Translation;
			Ray<float> direct( start, Translation );

			float offset = 0.0;
			ushort colls = 0;
			Collision coll;
			do {
				coll = collide( direct );

				result.push_back( rho - coll.t - offset );
				result.push_back( (float)coll.index );

				offset += coll.t + (float)G_EPSILON * 2;
				direct.start += direct.direct * ( coll.t + (float)G_EPSILON * 2 );
				colls++;

			} while( coll && colls < coll_per_step );

			while( colls < coll_per_step ) {
				result.push_back( 0.0f );	result.push_back(-1.0f);
				colls++;
			}

		}
	}

	return result;
}


void Geometry::draw() {
	if( !Enabled )
		return;

	_Renderer->vertex_source_proje( Vertices );

	DrawCallInfo info( Renderer::TRI, -1, Translation );
	if( Indices.size() )	_Renderer->draw_indices_proje( Indices, info );
	else					_Renderer->draw_vertices_proje( info );

	_Renderer->release_vertex_source();
}

Collision Geometry::collide( const Geometry& other ) const {
	Collision col;
	if( !Enabled || !other.Enabled )
		return col;

	for( size_t i = 0; i < Indices.size() || i < Vertices.size(); i += 3 ) {
		const Vector3f& p1 = Vertices[ Indices.size()?Indices[i]:i ].Coordinates + Translation, 
						p2 = Vertices[ Indices.size()?Indices[i+1]:i+1 ].Coordinates + Translation,
						p3 = Vertices[ Indices.size()?Indices[i+2]:i+2 ].Coordinates + Translation;

		col = other.collide( Ray<float>( p1, p2 ) );
		if( col ) return col;

		col = other.collide( Ray<float>( p2, p3 ) );
		if( col ) return col;

		col = other.collide( Ray<float>( p3, p1 ) );
		if( col ) return col;
	}

	col = other.collide( Vertices[ 0 ].Coordinates );
	if( col )	return col;

	col = collide( other.Vertices[ 0 ].Coordinates );
	return col;
}

Collision Geometry::collide( const Ray<float>& ray ) const {
	Collision col;
	col.colliding_ray = ray;

	for( size_t i = 0; i < Indices.size() || i < Vertices.size(); i += 3 ) {
		const Vector3f& p1 = Vertices[ Indices.size()?Indices[i]:i ].Coordinates + Translation, 
						p2 = Vertices[ Indices.size()?Indices[i+1]:i+1 ].Coordinates + Translation,
						p3 = Vertices[ Indices.size()?Indices[i+2]:i+2 ].Coordinates + Translation;

		Vector3f u = p2 - p1, v = p3 - p1;
		Vector3f n = u.cross_product( v ).normalize(), to_tri = p1 - ray.start;

		float ray_to_normal = ray.direct.dot_product( n );
		if( fabs( ray_to_normal ) < G_EPSILON )
			continue;

		float to_tri_to_normal = to_tri.dot_product( n );
		float t = to_tri_to_normal / ray_to_normal;

		if( t < 0 || t > 1 )
			continue;

		Vector3f plane_point = ray.start + ray.direct * t;

		float dir = 0;
		dir = ( p2-p1 ).cross_product( plane_point - p1 ).dot_product( n );
		if( fabs( dir ) < G_EPSILON )	col.hit_ray = Ray<float>(p1, p2);
		if( dir < 0 )				continue;

		dir = ( p3-p2 ).cross_product( plane_point - p2 ).dot_product( n );
		if( fabs( dir ) < G_EPSILON )	col.hit_ray = Ray<float>(p2, p3);
		if( dir < 0 )				continue;

		dir = ( p1-p3 ).cross_product( plane_point - p3 ).dot_product( n );
		if( fabs( dir ) < G_EPSILON )	col.hit_ray = Ray<float>(p3, p1);
		if( dir < 0 )				continue;

		col.collision = true;
		col.t = t;
		col.index = i;
		col.normal = n;
		return col;
	}
	return col;
}

Collision Geometry::collide( const Vector3f& point ) const {
	Collision col;

	for( size_t i = 0; i < Indices.size() || i < Vertices.size(); i += 3 ) {
		const Vector3f& p1 = Vertices[ Indices.size()?Indices[i]:i ].Coordinates + Translation, 
						p2 = Vertices[ Indices.size()?Indices[i+1]:i+1 ].Coordinates + Translation,
						p3 = Vertices[ Indices.size()?Indices[i+2]:i+2 ].Coordinates + Translation;

		Vector3f u = p2 - p1, v = p3 - p1;

		Vector3f n = u.cross_product( v ).normalize();
		float d = -n.dot_product( p1 );

		float eval = n.dot_product( point ) + d;
		if( eval > 0 )
			return col;
	}

	col.collision = true;
	return col;
}



