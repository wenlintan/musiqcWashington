
#include "roam.hpp"
#include "renderer.hpp" // for camera pos access

#include <algorithm>

#include <boost/range/irange.hpp>
#include <boost/python.hpp>
#include "python_wrap_utils.hpp"

const float split_size = 0.707106f;
//const float split_size = 0.5;
using namespace boost::python;

void wrap_roam() {

	boost_function_from_python< float(float, float, float) >();
	class_< VertexArray, VertexArray::pointer_type, bases<Mesh>,
		boost::noncopyable >( "VertexArray",
		init<size_t, size_t>() )
		;

	class_< SphericalROAM, SphericalROAM::pointer_type,
			bases<Component>, boost::noncopyable >( "SphericalROAM", 
			init<SphericalROAM::callback_t>() )
		;

	class_< SphericalROAMSystem, SphericalROAMSystem::pointer_type,
			bases<System>, boost::noncopyable >( "SphericalROAMSystem" )
		.def( "update", &SphericalROAMSystem::update )
		;

}

VertexArray::VertexArray( size_t nvertices_, size_t ntriangles ): 
		nvertices( nvertices_ ), nused_vertices(0), 
		nindices( ntriangles*3 ), nused_indices(0)
{
	data = (unsigned char*)allocate_data<attrib_t>( nvertices );
	indices = (index_t*)allocate_index_data<index_t>(ntriangles*3);

	for( size_t i = 0; i < attrib_size*nvertices; ++i )
		data[ i ] = 0;

	for( size_t i = 0; i < 3*ntriangles; ++i )
		indices[ i ] = 0;

	boost::integer_range<size_t> ir = boost::irange<size_t>(0, nvertices);
	free_vertices.assign( ir.begin(), ir.end() );

	ir = boost::irange<size_t>(0, ntriangles);
	free_indices.assign( ir.begin(), ir.end() );
}

size_t VertexArray::add_vertex( const Vector3f& position, 
	const Vector3f& normal_ ) {

	if( free_vertices.empty() ) {
		exit( 0 );
		return (size_t)-1;
	}

	size_t index = free_vertices.back();
	free_vertices.pop_back();
	++nused_vertices;

	float* cvertex = vertex( index );
	cvertex[0] = position.d[0];
	cvertex[1] = position.d[1];
	cvertex[2] = position.d[2];

	float* cnormal = normal( index );
	cnormal[0] = normal_.d[0];
	cnormal[1] = normal_.d[1];
	cnormal[2] = normal_.d[2];
	return index;
}

size_t VertexArray::add_triangle( size_t i1, size_t i2, size_t i3 ) {
	if( free_indices.empty() ) {
		return (size_t)-1;
	}

	size_t index = free_indices.back();
	free_indices.pop_back();
	++nused_indices;

	update_triangle( index, i1, i2, i3 );
	return index;
}

void VertexArray::update_triangle( size_t index,
	size_t i1, size_t i2, size_t i3 ) {

	if( i1 > nvertices || i2 > nvertices || i3 > nvertices )
		std::cout << "ERROR" << std::endl;

	indices[ index*3 + 0 ] = (index_t)i1;
	indices[ index*3 + 1 ] = (index_t)i2;
	indices[ index*3 + 2 ] = (index_t)i3;
}

void VertexArray::remove_point( size_t index ) {
	free_vertices.push_back( index );
	--nused_vertices;
}

void VertexArray::remove_triangle( size_t index ) {
	free_indices.push_back( index );
	--nused_indices;

	update_triangle( index, 0, 0, 0 );
}

float PriorityData::priority( const Vector3f& pos, const Vector3f& look ) {
	float dist = std::max( 0.00001f, 
		(midpoint_vector - pos).length_sq() );
	float dp = pos.dot( midpoint_vector ) / pos.length() / 
		midpoint_vector.length() + 1.0f;
	if( midpoint_vector.length_sq() < 0.999 ) 
		dist *= 10.f;
	return depth / dist * dp;
}

Diamond::Diamond(): free( false ), dirty( true ) {
	children[0] = children[1] = 0;
}

Diamond::~Diamond() {
	std::cout << "Bye bye." << std::endl;
	if( children[0] )
		children[0]->parent->diamond = children[0]->diamond = 0;
	if( children[1] )
		children[1]->parent->diamond = children[1]->diamond = 0;
}

bool Diamond::initialize( VertexArray& va, Triangle* base ) {

	free = false; dirty = true;
	//if( !base->parent )
	//	return false;

	if( base->parent == base->neighbors[1] )
		base = base->neighbors[1];

	if( base->diamond ) 
		std::cout << "Bad diamond." << std::endl;
	//if( !base->neighbors[0]->parent || !base->neighbors[1]->parent )
	//	return false;

	children[0] = base->neighbors[0];
	children[1] = base->neighbors[1];

	children[0]->parent->diamond = children[1]->parent->diamond =
		children[0]->diamond = children[1]->diamond = this;

	priority_data.midpoint_vector = Vector3f(
		va.vertex( va.triangle( base->index )[ 1 ] ) );
	priority_data.depth = base->priority_data.depth;
	return true;
}

void Diamond::initialize( VertexArray& va, Triangle* child1, 
	Triangle* child2 ) {

	free = false; dirty = true;
	children[0] = child1;
	children[1] = child2;

	if( child1->diamond )
		std::cout << "Bas diamond." << std::endl;

	child1->parent->neighbors[0] = child1;
	child1->neighbors[1] = child1->parent;
	child1->neighbors[0] = child2->parent;
	child2->parent->neighbors[1] = child1;
	child2->parent->neighbors[0] = child2;
	child2->neighbors[1] = child2->parent;
	child2->neighbors[0] = child1->parent;
	child1->parent->neighbors[1] = child2;

	children[0]->parent->diamond = children[1]->parent->diamond =
		children[0]->diamond = children[1]->diamond = this;

	priority_data.midpoint_vector = Vector3f(
		va.vertex( va.triangle( child1->index )[ 1 ] ) );
	priority_data.depth = child1->priority_data.depth;
}

void Diamond::clear() {
	children[0]->parent->diamond = children[0]->diamond = 0;
	children[1]->parent->diamond = children[1]->diamond = 0;
}

void Diamond::merge( VertexArray& va ) {
	if( children[0]->diamond != this )
		std::cout << "I have found the problem." << std::endl;

	size_t mid = va.triangle( children[0]->index )[ 1 ];
	va.remove_point( mid );

	children[0]->merge( va );
	children[1]->merge( va );

	children[0]->parent->diamond = children[0]->diamond = 0;
	children[1]->parent->diamond = children[1]->diamond = 0;
}

Triangle::Triangle( size_t index_ ): 
	index( index_ ), parent( 0 ), diamond( 0 ), dirty( true ), free( false )
{
	priority_data.depth = 1.0f;
}

void Triangle::set_neighbors( Triangle* n1, Triangle* n2, Triangle* n3 ) {
	neighbors[0] = n1;
	neighbors[1] = n2;
	neighbors[2] = n3;
}

bool Triangle::is_diamond() {
	return neighbors[0]->neighbors[0]->neighbors[0]->neighbors[0] == this;
}


Triangle* Triangle::split_first() {
	if( neighbors[2]->neighbors[2] == this ) 	return 0;
	return neighbors[2];
}

Diamond* Triangle::split( VertexArray& va, Triangle* new_tri, 
	size_t midpoint ) {

	//delete diamond;
	Diamond* dia = diamond;
	if( diamond ) diamond->clear();

	dirty = true;
	new_tri->free = false;
	new_tri->dirty = true;
	VertexArray::index_t* indices = va.triangle( index );
	
	//size_t new_tri_index = va.add_triangle( 
	//	indices[2], midpoint, indices[1] );

	//Triangle* new_tri = new Triangle( new_tri_index, this );
	new_tri->parent = this;
	va.update_triangle( new_tri->index, indices[2], midpoint, indices[1] );
	va.update_triangle( index, indices[1], midpoint, indices[0] );

	neighbors[2] = neighbors[0];
	new_tri->neighbors[2] = neighbors[1];
	if( neighbors[1]->neighbors[2] == this ) {
		neighbors[1]->neighbors[2] = new_tri;
	} else if( neighbors[1]->neighbors[1] == this ) {
		std::cout << "Poop." << std::endl;
		neighbors[1]->neighbors[1] = new_tri;
	} else {
		neighbors[1]->neighbors[0] = new_tri;
	}

	new_tri->priority_data.depth = priority_data.depth * split_size;
	priority_data.depth *= split_size;

	new_tri->priority_data.midpoint_vector = priority_data.midpoint_vector =
		Vector3f( va.vertex( midpoint ) );

	return dia;
}

void Triangle::merge( VertexArray& va ) {

	free = dirty = true;
	parent->dirty = true;

	VertexArray::index_t* indices = va.triangle( index );
	VertexArray::index_t* pindices = va.triangle( parent->index );
	va.update_triangle( parent->index, pindices[2], 
		pindices[0], indices[0] );
	va.update_triangle( index, 0, 0, 0 );

	parent->set_neighbors( parent->neighbors[2],
		neighbors[2], neighbors[0] );
	parent->priority_data.midpoint_vector = 
		Vector3f( va.vertex( pindices[0] ) );
	parent->priority_data.depth /= split_size;

	if( neighbors[2]->neighbors[2] == this )
		neighbors[2]->neighbors[2] = parent;
	else if( neighbors[2]->neighbors[1] == this )
		neighbors[2]->neighbors[1] = parent;
	else
		neighbors[2]->neighbors[0] = parent;

	//va.remove_triangle( index );
}

SphericalROAM::SphericalROAM( callback_t map_ ): 
	Component( Component::ROAM ), map( map_ ), initialized( false ), 
	nfree_triangles( 0 )
{}

void SphericalROAMSystem::update( Entity::pointer_type ent ) {
	if( ent->has_component( Component::Camera ) ) {
		pos = ent->transform().position;
	}

	if( !ent->has_component( Component::Mesh ) ) return;
	if( !ent->has_component( Component::Texture ) ) return;
	VertexArray& array = static_cast<VertexArray&>(ent->mesh() );
	SphericalROAM& roam = static_cast<SphericalROAM&>(
		ent->get_component( Component::ROAM ) );

	Vector3f look;
	if( !roam.initialized )
		initial_geometry( roam, array );

	//std::cout << "Verifying" << std::endl;
	check_diamonds( roam );

	std::vector< TriangleData >::iterator titer = roam.splits.begin();
	for(; titer != roam.splits.end(); ++titer )
		titer->update( pos, look );

	std::vector< DiamondData >::iterator diter = roam.merges.begin();
	for(; diter != roam.merges.end(); ++diter )
		diter->update( pos, look );

	std::make_heap( roam.splits.begin(), roam.splits.end() );
	std::make_heap( roam.merges.begin(), roam.merges.end() );

	//std::cout << "Starting split." << std::endl;
	size_t nsplits = 0;
	//std::vector< Triangle* > split_queue;
	
	bool merging = false;
	while( roam.splits.front().priority > 2*roam.merges.front().priority &&
		nsplits < 1000 ) {

		while( roam.nfree_triangles < 128 ) {
			DiamondData dd = roam.merges.front();
			while( dd.dirty() ) {
				std::pop_heap( roam.merges.begin(), roam.merges.end() );
				roam.merges.pop_back();
				dd.update( pos, look );
				roam.merges.push_back( dd );
				std::push_heap( roam.merges.begin(), roam.merges.end() );
				dd = roam.merges.front();
			}

			std::pop_heap( roam.merges.begin(), roam.merges.end() );
			roam.merges.pop_back();
			merge( roam, array, dd.diamond );
			dd.update( pos, look );
			roam.merges.push_back( dd );
			std::push_heap( roam.merges.begin(), roam.merges.end() );
		}

		TriangleData td = roam.splits.front();
		while( td.dirty() ) {
			std::pop_heap( roam.splits.begin(), roam.splits.end() );
			roam.splits.pop_back();
			td.update( pos, look );
			roam.splits.push_back( td );
			std::push_heap( roam.splits.begin(), roam.splits.end() );
			td = roam.splits.front();
		}

		std::pop_heap( roam.splits.begin(), roam.splits.end() );
		roam.splits.pop_back();
		split( roam, array, td.triangle );
		td.update( pos, look );
		roam.splits.push_back( td );
		std::push_heap( roam.splits.begin(), roam.splits.end() );

		++nsplits;
	}

	/*
	while( nsplits < 1000 ) {
		//std::cout << "Merges " << roam.merges.size() << std::endl;
		TriangleData td = roam.splits.front();
		while( td.dirty() ) {
			std::pop_heap( roam.splits.begin(), roam.splits.end() );
			roam.splits.pop_back();
			td.update( pos, look );
			roam.splits.push_back( td );
			std::push_heap( roam.splits.begin(), roam.splits.end() );
			td = roam.splits.front();
		}
		std::pop_heap( roam.splits.begin(), roam.splits.end() );
		roam.splits.pop_back();

		Triangle* trisplit = td.triangle;
		do { 
			split_queue.push_back( trisplit ); 
			Diamond* dia = trisplit->diamond;
			if( dia ) {
				dia->clear();
				roam.free_diamond( dia );
			}
		} while( trisplit = trisplit->split_first() );

		DiamondData dd = roam.merges.front();
		//std::cout << "Queue " << split_queue.size() << std::endl;
		do {
			trisplit = split_queue.back();
			split_queue.pop_back();

			while( dd.dirty() || dd.diamond->free ) {
				//std::cout << "Dirty " << roam.merges.size() << std::endl;
				std::pop_heap( roam.merges.begin(), roam.merges.end() );
				roam.merges.pop_back();
				if( !dd.diamond->free ) {
					dd.update( pos, look );
					roam.merges.push_back( dd );
					std::push_heap( roam.merges.begin(), roam.merges.end() );
				}
				dd = roam.merges.front();
			}

			//std::cout << "Got" << std::endl;
			if( td.priority < dd.priority * 2 )	break;
			std::pop_heap( roam.merges.begin(), roam.merges.end() );
			roam.merges.pop_back();

			split( roam, array, *trisplit, *dd.diamond );
			dd = roam.merges.front();
			++nsplits;
		} while( split_queue.size() );

		if( td.priority < dd.priority * 2 )	break;
		td.update( pos, look );
		roam.splits.push_back( td );
		std::push_heap( roam.splits.begin(), roam.splits.end() );
	}

	*/
	std::cout << "Split " << nsplits << std::endl;
	return;
}

void SphericalROAMSystem::merge( SphericalROAM& roam,
	VertexArray& array, Diamond* dia ) {

	dia->merge( array );
	for( unsigned char i = 0; i < 2; ++i ) {
		Triangle* par = dia->children[i]->parent;
		if( par->parent && par->is_diamond() ) {
			Diamond* newdia = roam.get_free_diamond();
			if( !newdia->initialize( array, par ) ) {
				roam.free_diamond( newdia );
				continue;
			}
			//roam.merges.push_back( DiamondData( newdia ) );
			//std::push_heap( roam.merges.begin(), roam.merges.end() );
		}
		//if( check_diamonds( roam ) > 1 )
		//	std::cout << "I did it." << std::endl;
	}
	roam.free_diamond( dia );

	roam.triangles.remove( dia->children[0] );
	roam.triangles.remove( dia->children[1] );
	roam.free_triangles.push_back( dia->children[0] );
	roam.free_triangles.push_back( dia->children[1] );
	roam.nfree_triangles += 2;
}

void SphericalROAMSystem::split( SphericalROAM& roam, 
	VertexArray& array, Triangle* tri ) {

	if( tri->split_first() ) {
		split( roam, array, tri->split_first() );
	}

	/*
	if( !dia.children[0]->is_diamond() )
		std::cout << "No diamond." << std::endl;

	dia.merge( array );
	Triangle* parents[2];
	for( unsigned char i = 0; i < 2; ++i ) {
		Triangle* par = parents[i] = dia.children[i]->parent;
		if( par->parent && par->is_diamond() ) {
			Diamond* newdia = roam.get_free_diamond();
			if( !newdia->initialize( array, par ) ) {
				roam.free_diamond( newdia );
				continue;
			}
			roam.merges.push_back( DiamondData( newdia ) );
			std::push_heap( roam.merges.begin(), roam.merges.end() );
		}
		//if( check_diamonds( roam ) > 1 )
		//	std::cout << "I did it." << std::endl;
	}

	while( queue.back()->split_first() ) {
		queue.push_back( queue.back()->split_first() );
		//array.remove_triangle( dia.children[0]->index );
		//array.remove_triangle( dia.children[1]->index );
		//roam.free_diamond( &dia );
		//return;
	}
		
	Triangle& tri = *queue.back();
	queue.pop_back();
	*/

	Triangle* news[2];
	news[0] = &roam.free_triangles.back();
	roam.free_triangles.pop_back();
	news[1] = &roam.free_triangles.back();
	roam.free_triangles.pop_back();

	roam.triangles.push_back( news[0] );
	roam.triangles.push_back( news[1] );
	roam.nfree_triangles -= 2;

	VertexArray::index_t* indices = array.triangle( tri->index );
	Vector3f midpoint_dir = Vector3f( array.vertex( indices[0] ) ) +
		Vector3f( array.vertex( indices[2] ) );
	size_t vert = get_vertex( roam, array, midpoint_dir );

	Diamond* frees[2];
	frees[0] = tri->neighbors[2]->split( array, news[1], vert );
	frees[1] = tri->split( array, news[0], vert );

	for( unsigned char i = 0; i < 2; ++i ) {
		roam.free_diamond( frees[i] );
	}

	Diamond* newdia = roam.get_free_diamond();
	newdia->initialize( array, news[0], news[1] );

	//roam.merges.push_back( DiamondData( newdia ) );
	//std::push_heap( roam.merges.begin(), roam.merges.end() );
	//roam.free_diamond( &dia );

	//if( check_diamonds( roam ) )
	//	std::cout << "I did it." << std::endl;
}

size_t SphericalROAMSystem::get_vertex( SphericalROAM& roam, 
	VertexArray& array, Vector3f& normal ) {

	float h = 1.f, l = normal.length();
	float off = roam.map( 1.f + normal.d[0]/l,
		1.f + normal.d[1]/l, 1.f + normal.d[2]/l ); 

	Vector3f n = normal / l;
	normal *= ((h+off) / normal.length());

	float off_map = ( off + 0.1f ) / 0.2f;
	unsigned char color = 255;//(unsigned char)( off_map*255 );
	Vector3ub c( color, color, color );

	Vector3f t( 0.0f, 1.0f, 0.0f );
	if( fabsf( n.d[1] ) > 0.85 )
		 t = Vector3f( 1.0f, 0.0f, 0.0f );
	Vector3f u = n.cross( t );
	Vector3f v = n.cross( u );

	const float dperp = 0.000001f;
	Vector3f utemp = n + u*dperp;
	utemp /= utemp.length();
	float dndu = ( roam.map( 1.f + utemp.d[0],
		1.f + utemp.d[1], 1.f + utemp.d[2] ) - off ) / dperp;
	Vector3f vtemp = n + v*dperp;
	vtemp /= vtemp.length();
	float dndv = ( roam.map( 1.f + vtemp.d[0],
		1.f + vtemp.d[1], 1.f + vtemp.d[2] ) - off ) / dperp;

	Vector3f norm = n - u * dndu - v * dndv;
	norm /= norm.length();

	return array.add_vertex( normal, norm );
}

void SphericalROAMSystem::initial_geometry( SphericalROAM& roam,
	VertexArray& array ) {

	roam.initialized = true;

	size_t pts[6];
	pts[0] = get_vertex( roam, array, Vector3f( 0., 1., 0. ) );
	pts[1] = get_vertex( roam, array, Vector3f( 1., 0., 1. ) );
	pts[2] = get_vertex( roam, array, Vector3f( 1., 0., -1. ) );
	pts[3] = get_vertex( roam, array, Vector3f( -1., 0., -1. ) );
	pts[4] = get_vertex( roam, array, Vector3f( -1., 0., 1. ) );
	pts[5] = get_vertex( roam, array, Vector3f( 0., -1., 0. ) );

	size_t tris[8];
	tris[0] = array.add_triangle( pts[2], pts[0], pts[1] );
	tris[1] = array.add_triangle( pts[3], pts[0], pts[2] );
	tris[2] = array.add_triangle( pts[4], pts[0], pts[3] );
	tris[3] = array.add_triangle( pts[1], pts[0], pts[4] );
	tris[4] = array.add_triangle( pts[4], pts[5], pts[1] );
	tris[5] = array.add_triangle( pts[3], pts[5], pts[4] );
	tris[6] = array.add_triangle( pts[2], pts[5], pts[3] );
	tris[7] = array.add_triangle( pts[1], pts[5], pts[2] );

	Triangle* ts[8];
	for( size_t i = 0; i < 8; ++i ) {
		ts[ i ] = new Triangle( tris[i] );
		roam.triangles.push_back( ts[ i ] );
		roam.splits.push_back( TriangleData( ts[i] ) );
		std::push_heap( roam.splits.begin(), roam.splits.end() );
	}

	ts[0]->set_neighbors( ts[1], ts[3], ts[7] );
	ts[1]->set_neighbors( ts[2], ts[0], ts[6] );
	ts[2]->set_neighbors( ts[3], ts[1], ts[5] );
	ts[3]->set_neighbors( ts[0], ts[2], ts[4] );
	ts[4]->set_neighbors( ts[5], ts[7], ts[3] );
	ts[5]->set_neighbors( ts[6], ts[4], ts[2] );
	ts[6]->set_neighbors( ts[7], ts[5], ts[1] );
	ts[7]->set_neighbors( ts[4], ts[6], ts[0] );

	for( size_t i = 0; i < 4; ++i )		
		ts[ i ]->priority_data.midpoint_vector = Vector3f( 0., 1., 0. );
	for( size_t i = 4; i < 8; ++i )		
		ts[ i ]->priority_data.midpoint_vector = Vector3f( 0., -1., 0. );

	Vector3f look;
	size_t ndirty = 0;
	std::vector< Triangle* > split_queue;
	while( array.nvertices - array.nused_vertices ) {
		TriangleData d = roam.splits.front();
		std::pop_heap( roam.splits.begin(), roam.splits.end() );
		roam.splits.pop_back();

		if( d.dirty() ) {
			d.update( pos, look );
			roam.splits.push_back( d );
			std::push_heap( roam.splits.begin(), roam.splits.end() );
			++ndirty;
			continue;
		}

		Triangle* split = d.triangle;
		do { 
			split_queue.push_back( split ); 
		} while( split = split->split_first() );

		do {
			split = split_queue.back();
			split_queue.pop_back();

			VertexArray::index_t* indices = array.triangle( split->index );
			Vector3f midpoint_dir = Vector3f( array.vertex( indices[0] ) ) +
				Vector3f( array.vertex( indices[2] ) );
			size_t new_vert = get_vertex( roam, array, midpoint_dir );

			Triangle* tri1 = new Triangle( array.add_triangle( 0, 0, 0 ) );
			Triangle* tri2 = new Triangle( array.add_triangle( 0, 0, 0 ) );
			roam.triangles.push_back( tri1 );
			roam.triangles.push_back( tri2 );

			Diamond* frees[2];
			frees[0] = split->neighbors[2]->split( array, tri2, new_vert );
			frees[1] = split->split( array, tri1, new_vert );

			for( unsigned char i = 0; i < 2; ++i ) {
				roam.free_diamond( frees[i] );
			}

			Diamond* diamond = roam.get_free_diamond();
			diamond->initialize( array, tri1, tri2 );

			//roam.merges.push_back( DiamondData( diamond, pos, look ) );
			//std::push_heap( roam.merges.begin(), roam.merges.end() );
			roam.splits.push_back( TriangleData( tri1, pos, look ) );
			std::push_heap( roam.splits.begin(), roam.splits.end() );
			roam.splits.push_back( TriangleData( tri2, pos, look ) );
			std::push_heap( roam.splits.begin(), roam.splits.end() );

		} while( array.nvertices - array.nused_vertices && 
			split_queue.size() );

		d.update( pos, look );
		roam.splits.push_back( d );
		std::push_heap( roam.splits.begin(), roam.splits.end() );
	}
}

size_t SphericalROAMSystem::check_diamonds( SphericalROAM& roam ) {

	size_t nfails = 0;
	SphericalROAM::dia_iter_t diter = roam.diamonds.begin();
	while( diter != roam.diamonds.end() ) {
		Diamond* dia = &*diter;
		if( dia->children[0]->diamond != dia ||
			dia->children[1]->diamond != dia ||
			dia->children[0]->parent->diamond != dia ||
			dia->children[1]->parent->diamond != dia )
			std::cout << "Bad linkage." << std::endl;

		if( !diter->children[0]->is_diamond() ) {
			std::cout << "No diamond." << std::endl;
			++nfails;
		}
		if( diter->free ) {
			std::cout << "It is free." << std::endl;
		}
		++diter;
	}

	diter = roam.free_diamonds.begin();
	for( ; diter != roam.free_diamonds.end(); ++diter ) {
		if( !diter->free ) {
			std::cout << "It is not free." << std::endl;
		}
	}

	return nfails;
}

