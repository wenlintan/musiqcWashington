
#include "roam.hpp"
#include <iostream>
#include <cstdlib> // Temporary for rand

#include <boost/cstdint.hpp>
#include <boost/range/irange.hpp>
#include <boost/functional/value_factory.hpp>
#include <boost/lambda/lambda.hpp>
#include <boost/preprocessor/repetition/enum_params.hpp>

#include <boost/python.hpp>
#include <boost/python/suite/indexing/map_indexing_suite.hpp>

using namespace boost::python;

template< typename Wrap >
struct ctypes_type {
};

template<>
struct ctypes_type< float[3] > {
	static object type( object ctypes ) {
		object base = ctypes.attr("c_float") * 3;
		return ctypes.attr("POINTER")( base );
	}
};

template<>
struct ctypes_type< unsigned char[4] > {
	static object type( object ctypes ) {
		object base = ctypes.attr("c_ubyte") * 4;
		return ctypes.attr("POINTER")( base );
	}
};

template<>
struct ctypes_type< unsigned short > {
	static object type( object ctypes ) {
		object base = ctypes.attr("c_ushort");
		return ctypes.attr("POINTER")( base );
	}
};

template< class T, typename Wrap, Wrap* (T::*member)() >
struct CTypesWrapper {
	static object wrap( T* elem ) {
		object ctypes = import( "ctypes" );
		Wrap* data = (elem->*member)();
		long_ addr( (boost::uint64_t)data );

		return ctypes.attr("cast")( 
			addr, ctypes_type<Wrap>::type( ctypes ) );
	}
};

template<class Key, class Val>
struct map_item
{
	typedef std::map<Key,Val> Map;

	static Val& get(Map& self, const Key idx) {
		if( self.find(idx) != self.end() ) return self[idx];
		PyErr_SetString(PyExc_KeyError,"Map key not found");
		throw_error_already_set();

		// Should never happen
		return self[idx];
	}

	static void set(Map& self, const Key idx, const Val val) { 
		self[idx]=val; 
	}

	static void del(Map& self, const Key n) { 
		self.erase(n);
	}

	static bool in(Map const& self, const Key n) { 
		return self.find(n) != self.end(); 
	}

	static list keys(Map const& self) {
		list t;
		for(Map::const_iterator it=self.begin(); it!=self.end(); ++it)
			t.append(it->first);
		return t;
	}

	static list values(Map const& self) {
		list t;
		for(Map::const_iterator it=self.begin(); it!=self.end(); ++it)
			t.append(it->second);
		return t;
	}

	static list items(Map const& self) {
		list t;
		for(Map::const_iterator it=self.begin(); it!=self.end(); ++it)
			t.append( make_tuple(it->first, it->second) );
		return t;
	}

	static list iteritems(Map const& self) { return items(self); }
};

template< typename T >
T* unwrap_address( object o ) {
	boost::uint64_t addr = extract<boost::uint64_t>( o );
	T* ptr = (T*)addr;
	return ptr;
}

template< typename T >
T unwrap_vector( object o ) {
	object ctypes = import("ctypes");
	object contents = o.attr("contents");
	boost::uint64_t addr = extract<boost::uint64_t>(
		ctypes.attr("addressof")( contents ) );
	return T( (T::value_type*)addr );
}

void wrap_update( SphericalROAM* roam, dict data, object user ) {
	roam->dynamic_update( 
		unwrap_address<SphericalROAM::vertex_t>( data[0] ),
		unwrap_address<SphericalROAM::color_t>( data[2] ),
		unwrap_address<SphericalROAM::index_t>( data[100] ),
		unwrap_vector<Vector3f>( user[0] ),
		unwrap_vector<Vector3f>( user[1] )  );
}

template< typename Signature >
struct boost_function_from_python {};

template< typename R, BOOST_PP_ENUM_PARAMS( 3, typename T ) >
struct boost_function_from_python
	< R ( BOOST_PP_ENUM_PARAMS(3, T) ) > 
{

	typedef boost::function< R ( BOOST_PP_ENUM_PARAMS(3, T) ) > 
		wrapped_type;

	boost_function_from_python() {
		converter::registry::push_back(
			&convertible,
			&construct,
			type_id< wrapped_type >() );
	}

	static void* convertible( PyObject* obj_ptr ) {
		if( !PyCallable_Check( obj_ptr ) )	return 0;
		return obj_ptr;
	}

	static void construct( PyObject* obj_ptr,
		converter::rvalue_from_python_stage1_data* data ) {

		void* storage = (
			(converter::rvalue_from_python_storage<
				wrapped_type >*)data)->storage.bytes;

		boost::function< object ( BOOST_PP_ENUM_PARAMS(3, T) ) >
			obj = boost::function< object ( BOOST_PP_ENUM_PARAMS(3, T) ) >
				( object( handle<>(borrowed(obj_ptr) )) );

		new (storage) wrapped_type(
			boost::bind< R >( boost::value_factory<extract<R> >(),
			boost::bind< object >( obj,
				boost::lambda::_1, boost::lambda::_2, 
				boost::lambda::_3 ) ) );
		data->convertible = storage;
	}
};

BOOST_PYTHON_MODULE( roam ) {

	typedef std::map<size_t, size_t> batch_data_dict;
	typedef map_item<size_t, size_t> batch_data_wrap;

	class_< batch_data_dict >("batch_data_dict")
		.def("__len__", &batch_data_dict::size)
		.def("__getitem__", &batch_data_wrap().get, 
				return_value_policy<copy_non_const_reference>() )
		.def("__setitem__", &batch_data_wrap().set)
		.def("__delitem__", &batch_data_wrap().del)
		.def("clear", &batch_data_dict::clear)
		.def("__contains__", &batch_data_wrap().in)
		.def("has_key", &batch_data_wrap().in)
		.def("keys", &batch_data_wrap().keys)
		.def("values", &batch_data_wrap().values)
		.def("items", &batch_data_wrap().items)
		.def("iteritems", &batch_data_wrap().iteritems)
		;

	boost_function_from_python< float(float, float, float) >();
	class_< SphericalROAM >( "SphericalROAM", 
			init<size_t, size_t, SphericalROAM::callback_t>() )
		.def_readwrite( "batch_data", &SphericalROAM::batch_data )
		.def_readwrite( "update", &SphericalROAM::update )
		.def( "dynamic_update", wrap_update )

		.def( "set_offsets", &SphericalROAM::set_offsets )
		.def_readwrite( "nvertices", &SphericalROAM::nvertices )
		.def_readwrite( "nindices", &SphericalROAM::nindices )

		.def( "vertices", 
				CTypesWrapper< SphericalROAM, float[3], 
					&SphericalROAM::vertices >::wrap )
		.def( "colors", 
				CTypesWrapper< SphericalROAM, unsigned char[4],
					&SphericalROAM::colors >::wrap )
		.def( "indices",
				&CTypesWrapper< SphericalROAM, unsigned short,
					&SphericalROAM::indices >::wrap )
		;

}

VertexArray::VertexArray( size_t nvertices, size_t ntriangles,
		boost::function<float( float, float, float)> map_ ): 
		map( map_ ), mirror_vertices(0), mirror_colors(0),
		mirror_indices(0), nused_vertices(0), nused_indices(0)
{
	vertices = new float[ nvertices ][3];
	colors = new unsigned char[ nvertices ][4];
	indices = new unsigned short[ 3*ntriangles ];

	for( size_t i = 0; i < nvertices; ++i ) {
		vertices[i][0] = vertices[i][1] = vertices[i][2] = 0.f;
		colors[i][0] = colors[i][1] = colors[i][2] = colors[i][3] = 0;
	}

	for( size_t i = 0; i < 3*ntriangles; ++i )
		indices[ i ] = 0;

	boost::integer_range<size_t> ir = boost::irange<size_t>(0, nvertices);
	free_vertices.assign( ir.begin(), ir.end() );

	ir = boost::irange<size_t>(0, ntriangles);
	free_indices.assign( ir.begin(), ir.end() );
}

size_t VertexArray::add_point( Vector3f& normal ) {
	if( free_vertices.empty() ) {
		exit( 0 );
		return (size_t)-1;
	}

	size_t index = free_vertices.back();
	free_vertices.pop_back();
	++nused_vertices;

	float h = 10.f, l = normal.length();
	float off = map( 1.f + normal.d[0]/l,
		1.f + normal.d[1]/l, 1.f + normal.d[2]/l ); 

	normal *= ((h+off) / normal.length());

	float off_map = ( off + 3.f ) / 6.f;
	unsigned char color = (unsigned char)( off_map*255 );
	Vector3ub c( color, color, color );

	vertices[ index ][0] = normal.d[0];
	vertices[ index ][1] = normal.d[1];
	vertices[ index ][2] = normal.d[2];

	if( mirror_vertices ) {
		mirror_vertices[ index ][0] = normal.d[0];
		mirror_vertices[ index ][1] = normal.d[1];
		mirror_vertices[ index ][2] = normal.d[2];
	}

	colors[ index ][ 0 ] = c.d[0];
	colors[ index ][ 1 ] = c.d[1];
	colors[ index ][ 2 ] = c.d[2];
	colors[ index ][ 3 ] = 0;

	if( mirror_colors ) {
		mirror_colors[ index ][0] = c.d[0];
		mirror_colors[ index ][1] = c.d[1];
		mirror_colors[ index ][2] = c.d[2];
		mirror_colors[ index ][3] = 0;
	}

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

	if( i1 > 50000 || i2 > 50000 || i3 > 50000 )
		std::cout << "ERROR" << std::endl;

	indices[ index*3 + 0 ] = i1;
	indices[ index*3 + 1 ] = i2;
	indices[ index*3 + 2 ] = i3;

	if( mirror_indices ) {
		mirror_indices[ index*3 + 0 ] = i1;
		mirror_indices[ index*3 + 1 ] = i2;
		mirror_indices[ index*3 + 2 ] = i3;
	}
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
	float dist = std::max( 0.01f, (midpoint_vector - pos).length() );
	return diff / dist;
}

Diamond::Diamond( Triangle* base ) {
	if( base->parent == base->neighbors[1] )
		base = base->neighbors[1];

	parents[0] = base;
	parents[1] = base->neighbors[1]->neighbors[1];
	children[0] = base->neighbors[0];
	children[1] = base->neighbors[1];

	parents[0]->diamond = parents[1]->diamond =
		children[0]->diamond = children[1]->diamond = this;
}

Diamond::~Diamond() {
}

float Diamond::priority( const Vector3f& pos, const Vector3f& look ) {
	return priority_data.priority( pos, look );
}

void Diamond::clear() {
	parents[0]->diamond = parents[1]->diamond =
		children[0]->diamond = children[1]->diamond = 0;
}

void Diamond::merge( VertexArray& va ) {
	//std::cout << va.nused_vertices << std::endl;

	VertexArray::index_t* indices = va.indices;
	size_t mid = indices[ parents[0]->index*3 + 1 ];
	va.remove_point( mid );

	//std::cout << "Merge " << parents[0]->index << std::endl;

	children[0]->merge( va );	delete children[0];
	children[1]->merge( va );	delete children[1];

	parents[0]->add_midpoint( va );
	parents[1]->steal_midpoint( parents[0] );

	for( size_t i = 0; i < 2; ++ i ) {
		if( parents[i]->parent && parents[i]->is_diamond() ) {
			Diamond* d = new Diamond( parents[i] );
			d->links.link( &links );

			d->priority_data.midpoint_vector = Vector3f(
				va.vertices[ va.indices[ parents[i]->index*3 + 1 ] ] );
			Vector3f pt = (
				Vector3f( 
				va.vertices[ va.indices[ parents[i]->index*3 + 0 ] ] ) +
				Vector3f(
				va.vertices[ va.indices[ parents[i]->parent->index*3 + 2 ] ] ) )
				* 0.5;
			d->priority_data.diff = fabs( pt.length() 
				- d->priority_data.midpoint_vector.length() );
		} else {
			parents[i]->diamond = 0;
		}
	}
}

Triangle::Triangle( size_t index_, Triangle* parent_ ): 
	index( index_ ), parent( parent_ ), diamond( 0 ) 
{
	if( parent )	links.link( &parent->links );
}

void Triangle::set_neighbors( Triangle* n1, Triangle* n2, Triangle* n3 ) {
	neighbors[0] = n1;
	neighbors[1] = n2;
	neighbors[2] = n3;
}

bool Triangle::is_diamond() {
	return neighbors[0]->neighbors[0]->neighbors[0]->neighbors[0] == this;
}

bool Triangle::can_split() {
	return neighbors[2]->neighbors[2] == this;
}

Triangle* Triangle::split_first() {
	return neighbors[2];
}

void Triangle::add_midpoint( VertexArray& va ) {
	VertexArray::index_t* indices = &va.indices[ index*3 ];
	Vector3f pt0( va.vertices[ indices[0] ] ),
			 pt2( va.vertices[ indices[2] ] );

	priority_data.midpoint_vector = (pt0 + pt2) * (1 / 2.);
	float l = priority_data.midpoint_vector.length();

	midpoint = va.add_point( priority_data.midpoint_vector );
	priority_data.diff = fabs( l - priority_data.midpoint_vector.length() );
}

void Triangle::steal_midpoint( Triangle* neighbor ) {
	priority_data = neighbor->priority_data;
	midpoint = neighbor->midpoint;
}

Triangle* Triangle::split_one( VertexArray& va ) {
	if( diamond ) {
		// HACK: clear will destroy our "diamond" member as well
		Diamond* temp = diamond;
		diamond->clear();
		delete temp;
	}

	if( midpoint >= 50000 ) {
		std:: cout << midpoint << " my bad." << std::endl;
	}

	VertexArray::index_t* indices = &va.indices[ index*3 ];
	
	size_t new_tri_index = va.add_triangle( 
		indices[2], midpoint, indices[1] );

	Triangle* new_tri = new Triangle( new_tri_index, this );
	va.update_triangle( index, indices[1], midpoint, indices[0] );

	if( neighbors[1]->neighbors[2] == this ) {
		neighbors[1]->neighbors[2] = new_tri;
		new_tri->steal_midpoint( neighbors[1] );
	} else {
		neighbors[1]->neighbors[0] = new_tri;
		new_tri->add_midpoint( va );
	}

	if( neighbors[0]->neighbors[2] == this ) 
			steal_midpoint( neighbors[0] );
	else	add_midpoint( va );

	return new_tri;
}

void Triangle::relink( Triangle* mine, Triangle* neigh ) {
	mine->set_neighbors( neighbors[2], this, neighbors[1] );
	set_neighbors( mine, neigh, neighbors[0] );
}

float Triangle::priority( const Vector3f& pos, const Vector3f& look ) {
	return priority_data.priority( pos, look );
}

Diamond* Triangle::split( VertexArray& va ) {
	//std::cout << va.nused_vertices << std::endl;

	PriorityData original = priority_data;

	//std::cout << "Split " << index << std::endl;

	Triangle* neigh = neighbors[2]->split_one( va );
	Triangle* mine = split_one( va );

	neighbors[2]->relink( neigh, mine );
	relink( mine, neigh );

	Diamond* result = new Diamond( this );
	result->priority_data = original;
	return result;
}

void Triangle::merge( VertexArray& va ) {
	if( neighbors[2]->neighbors[2] != this )
		va.remove_point( midpoint );
	if( parent->neighbors[2]->neighbors[2] != parent )
		va.remove_point( parent->midpoint );

	va.update_triangle( parent->index, 
			va.indices[ parent->index*3 + 2 ],
			va.indices[ parent->index*3 + 0 ],
			va.indices[ index*3 + 0 ] );

	parent->set_neighbors( parent->neighbors[2],
			neighbors[2], neighbors[0] );

	if( neighbors[2]->neighbors[2] == this )
		neighbors[2]->neighbors[2] = parent;
	else if( neighbors[2]->neighbors[1] == this )
		neighbors[2]->neighbors[1] = parent;
	else
		neighbors[2]->neighbors[0] = parent;

	va.remove_triangle( index );
}

SphericalROAM::SphericalROAM( size_t nv, size_t nt, callback_t map ): 
	array( nv, nt, map ), nvertices( nv ), nindices( nt*3 ), update( 1 ),
	height_map( map )
{
	batch_data[ 0 ] = 1;
	batch_data[ 2 ] = 2;
	batch_data[ 100 ] = 3;

	initial_geometry();
}

void SphericalROAM::dynamic_update( 
	vertex_t* vertices, color_t* colors, index_t* indices,
	const Vector3f& pos, const Vector3f& look ) {

	array.mirror_vertices = vertices;
	array.mirror_colors = colors;
	array.mirror_indices = indices;

	tri_iter_t iter = triangles.begin(), end = triangles.end();
	for(; iter != triangles.end(); ++iter ) {
		if( iter->priority( pos, look ) > 0.05 ) {
			split( *iter );
		}
	}

	dia_iter_t diter = diamonds.begin(), dend = diamonds.end();
	while( diter != diamonds.end() ) {
		if( diter->priority( pos, look ) < 0.05 ) {
			diter->merge( array );
			delete &*diter++;
		} else ++diter;
	}
}

void SphericalROAM::set_offsets( size_t nvertices, size_t nindices ) {
}


void SphericalROAM::split( Triangle& tri ) {
	if( !tri.can_split() )
		split( *tri.split_first() );

	Diamond* split = tri.split( array );
	if( split )		diamonds.push_back( split );
}

void SphericalROAM::initial_geometry() {
	size_t pts[6];
	pts[0] = array.add_point( Vector3f( 0., 1., 0. ) );
	pts[1] = array.add_point( Vector3f( 1., 0., 1. ) );
	pts[2] = array.add_point( Vector3f( 1., 0., -1. ) );
	pts[3] = array.add_point( Vector3f( -1., 0., -1. ) );
	pts[4] = array.add_point( Vector3f( -1., 0., 1. ) );
	pts[5] = array.add_point( Vector3f( 0., -1., 0. ) );

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
		triangles.push_back( ts[ i ] );
	}


	ts[0]->set_neighbors( ts[1], ts[3], ts[7] );
	ts[1]->set_neighbors( ts[2], ts[0], ts[6] );
	ts[2]->set_neighbors( ts[3], ts[1], ts[5] );
	ts[3]->set_neighbors( ts[0], ts[2], ts[4] );
	ts[4]->set_neighbors( ts[5], ts[7], ts[3] );
	ts[5]->set_neighbors( ts[6], ts[4], ts[2] );
	ts[6]->set_neighbors( ts[7], ts[5], ts[1] );
	ts[7]->set_neighbors( ts[4], ts[6], ts[0] );

	for( size_t i = 0; i < 4; ++i )		ts[ i ]->add_midpoint( array );
	for( size_t i = 4; i < 8; ++i )		ts[ i ]->steal_midpoint( ts[ 7 - i ] );

	/*
	split( *ts[0] );
	split( triangles.back() );
	//split( *ts[0] );
	//split( *ts[0] );

	diamonds.begin()->merge( array );
	delete &diamonds.front();

	split( *ts[0] );

	diamonds.begin()->merge( array );
	delete &diamonds.front();
	diamonds.begin()->merge( array );
	delete &diamonds.front();

	if( diamonds.begin() == diamonds.end() )
		std::cout << "ERROR" << std::endl;
	diamonds.begin()->merge( array );
	delete &diamonds.front();
	
	for( size_t i = 0; i < 1000; ++i ) {
		tri_iter_t iter = triangles.begin(), end = triangles.end();
		for( size_t j = 0; (j < rand() % array.nused_indices) && iter != end; ++iter );
		if( iter == end ) continue;
		split( *iter );
	}

	dia_iter_t iter = diamonds.begin();
	while( iter != diamonds.end() ) {
		iter->merge( array );
		delete &*iter++;
	}
	*/
}

