
#include <vector>
#include <map>
#include <iostream>

#include <boost/python.hpp>
#include <boost/function.hpp>

#include "vector.hpp"
#include "list.hpp"

#include "mesh.hpp"
#include "system.hpp"

void wrap_roam();
struct VertexArray: Mesh {
	typedef boost::shared_ptr<VertexArray> pointer_type;

	typedef float vertex_t[3];
	typedef float normal_t[3];
	typedef unsigned char color_t[4];
	typedef unsigned short index_t;

private:
	typedef boost::mpl::vector<
		boost::mpl::pair< 
			MeshVertexData::Attribute<MeshVertexData::VERTEX>, vertex_t >,
		boost::mpl::pair< 
			MeshVertexData::Attribute<MeshVertexData::COLOR>, color_t >,
		boost::mpl::pair<
			MeshVertexData::Attribute<MeshVertexData::NORMAL>, normal_t >
			> attrib_t;
	const static size_t attrib_size = sizeof(vertex_t) + sizeof(color_t) +
		sizeof(normal_t);

	unsigned char*		data;
	unsigned short*		indices;

	std::vector< size_t >	free_vertices, free_indices;

public:
	size_t	nvertices, nused_vertices, nindices, nused_indices;
	VertexArray( size_t nvertices, size_t ntriangles );
	
	float* vertex( size_t index ) {
		return (float*)( data + index*attrib_size);
	}

	unsigned char* color( size_t index ) {
		return data + index*attrib_size + sizeof(vertex_t);
	}

	float* normal( size_t index ) {
		return (float*)( data + index*attrib_size + sizeof(vertex_t)
			+ sizeof(color_t) );
	}

	index_t* triangle( size_t index ) {
		return &indices[ index*3 ];
	}

	size_t add_vertex( const Vector3f& vert, const Vector3f& normal );
	size_t add_triangle( size_t i1, size_t i2, size_t i3 );

	void update_triangle( size_t index, size_t i1, size_t i2, size_t i3 );

	void remove_point( size_t index );
	void remove_triangle( size_t index );
};

struct PriorityData {
	float diff, depth;
	Vector3f midpoint_vector;

	float priority( const Vector3f& pos, const Vector3f& look );
};

class Triangle;
class Diamond {

public:
	Triangle*		children[2];
	PriorityData	priority_data;
	bool			dirty, free;

	ListLink<Diamond>	links;

	Diamond();
	~Diamond();

	bool initialize( VertexArray& va, Triangle* base );
	void initialize( VertexArray& va, Triangle* child1, Triangle* child2 ); 
	void clear();

	float priority( const Vector3f& pos, const Vector3f& look ) {
		return priority_data.priority( pos, look );
	}

	void merge( VertexArray& va );
};

class Triangle {

public:
	Diamond*		diamond;
	PriorityData	priority_data;
	bool			dirty, free;

	size_t		index;	// index into main indices array	
	Triangle*	neighbors[3];
	Triangle*	parent;

	ListLink<Triangle> links;

	Triangle( size_t index );

	bool is_diamond();
	Triangle* split_first();

	float priority( const Vector3f& pos, const Vector3f& look ) {
		return priority_data.priority( pos, look );
	}

	void set_neighbors( Triangle* n1, Triangle* n2, Triangle* n3 );
	Diamond* split( VertexArray& va, Triangle* tri, size_t midpoint );
	void merge( VertexArray& va );
};

struct TriangleData {
	Triangle* triangle;
	bool free;
	float priority;

	TriangleData( Triangle* tri ): triangle( tri )
	{}

	TriangleData( Triangle* tri, const Vector3f& pos, const Vector3f& look ):
		triangle( tri )
	{
		update( pos, look );
	}

	bool operator <( const TriangleData& other ) const {
		if( free && !other.free )
			return true;
		else if( !free && other.free )
			return false;
		return priority < other.priority;
	}

	bool dirty() {
		return triangle->dirty;
	}

	void update( const Vector3f& pos, const Vector3f& look ) {
		triangle->dirty = false;
		free = triangle->free;
		priority = triangle->priority( pos, look );
	}
};

struct DiamondData {
	Diamond* diamond;
	bool free;
	float priority;

	DiamondData( Diamond* dia ): diamond( dia )
	{}

	DiamondData( Diamond* dia, const Vector3f& pos, const Vector3f& look ):
		diamond( dia )
	{
		update( pos, look );
	}

	bool operator <( const DiamondData& other ) const {
		if( free && !other.free )
			return true;
		else if( !free && other.free )
			return false;
		return priority > other.priority;
	}

	bool dirty() {
		return diamond->dirty;
	}

	void update( const Vector3f& pos, const Vector3f& look ) {
		diamond->dirty = false;
		free = diamond->free;
		priority = diamond->priority( pos, look );
	}
};

struct SphericalROAM: Component {
	typedef boost::shared_ptr< SphericalROAM > pointer_type;

	typedef List<Triangle, &Triangle::links> tri_list_t;
	typedef tri_list_t::iterator tri_iter_t;

	typedef List<Diamond, &Diamond::links> dia_list_t;
	typedef dia_list_t::iterator dia_iter_t;

	tri_list_t		triangles;
	dia_list_t		diamonds;

	size_t			nfree_triangles;
	tri_list_t		free_triangles;
	dia_list_t		free_diamonds;

	std::vector< TriangleData > splits;
	std::vector< DiamondData > merges;

	bool			initialized;
	typedef boost::function<float (float, float, float)> callback_t;
	callback_t		map;

	Diamond* get_free_diamond() {
		Diamond* d;
		if( !free_diamonds.empty() ) {
			d = &free_diamonds.back();
			free_diamonds.pop_back();
		} else {
			d = new Diamond();
			merges.push_back( DiamondData( d ) );
			std::push_heap( merges.begin(), merges.end() );
		}

		d->free = false;
		diamonds.push_back( d );
		return d;
	}

	void free_diamond( Diamond* d ) {
		if( !d ) return;
		d->dirty = d->free = true;
		diamonds.remove( d );
		free_diamonds.push_back( d );
	}

	SphericalROAM( callback_t map );
	void initial_geometry();
};

class SphericalROAMSystem: public System {
	Vector3f pos, look;	// location to refine ROAM around

	size_t check_diamonds( SphericalROAM& roam );

	void initial_geometry( SphericalROAM& roam, VertexArray& array );
	size_t get_vertex( SphericalROAM& roam, VertexArray& array, 
		Vector3f& dir );

	void merge( SphericalROAM& roam, VertexArray& array, Diamond* dia );
	void split( SphericalROAM& roam, VertexArray& array, Triangle* tri );

public:
	typedef boost::shared_ptr<SphericalROAMSystem> pointer_type;
	void update( Entity::pointer_type ent );

};

