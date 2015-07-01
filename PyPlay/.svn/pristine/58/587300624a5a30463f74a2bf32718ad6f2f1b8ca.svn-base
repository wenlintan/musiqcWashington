
#include <vector>
#include <map>
#include <iostream>

#include <boost/python.hpp>
#include <boost/function.hpp>

#include "vector.hpp"
#include "list.hpp"


struct VertexArray {
	typedef float vertex_t[3];
	typedef unsigned char color_t[4];
	typedef unsigned short index_t;

	typedef boost::function<float (float, float, float)> callback_t;

	float				(*vertices)[3];
	unsigned char		(*colors)[4];
	unsigned short*		indices;

	float				(*mirror_vertices)[3];
	unsigned char		(*mirror_colors)[4];
	unsigned short*		mirror_indices;

	callback_t			map;

	std::vector< size_t >	free_vertices, free_indices;
	size_t					nused_vertices, nused_indices;

	VertexArray( size_t nvertices, size_t ntriangles, callback_t map );
	
	size_t add_point( Vector3f& normal );
	size_t add_triangle( size_t i1, size_t i2, size_t i3 );

	void update_triangle( size_t index, size_t i1, size_t i2, size_t i3 );

	void remove_point( size_t index );
	void remove_triangle( size_t index );
};

struct PriorityData {
	float diff;
	Vector3f midpoint_vector;

	float priority( const Vector3f& pos, const Vector3f& look );
};

class Triangle;
class Diamond {
	Triangle*	parents[2];
	Triangle*	children[2];

	size_t			midpoint;

public:
	PriorityData	priority_data;

	ListLink<Diamond> links;
	Diamond( Triangle* base ); 
	~Diamond();

	float priority( const Vector3f& pos, const Vector3f& look );
	void merge( VertexArray& va );
	void clear();
};

class Triangle {
	Triangle* split_one( VertexArray& va );
	void relink( Triangle* mine, Triangle* theirs );

public:
	Diamond*	diamond;

	PriorityData	priority_data;
	size_t			midpoint;

	size_t		index;	// index into main indices array	
	Triangle*	neighbors[3];
	Triangle*	parent;

	ListLink<Triangle> links;

	Triangle( size_t index, Triangle* parent = 0 );

	void set_neighbors( Triangle* n1, Triangle* n2, Triangle* n3 );
	void add_midpoint( VertexArray& va );
	void steal_midpoint( Triangle* neighbor );

	bool is_diamond();
	bool can_split();
	Triangle* split_first();

	float priority( const Vector3f& pos, const Vector3f& look );
	Diamond* split( VertexArray& va );
	void merge( VertexArray& va );
};

class SphericalROAM {
	typedef List<Triangle, &Triangle::links> tri_list_t;
	typedef tri_list_t::iterator tri_iter_t;

	typedef List<Diamond, &Diamond::links> dia_list_t;
	typedef dia_list_t::iterator dia_iter_t;

	tri_list_t		triangles;
	dia_list_t		diamonds;

	VertexArray		array;
	void initial_geometry();
	void split( Triangle & tri );

public:
	typedef VertexArray::vertex_t vertex_t;
	typedef VertexArray::color_t color_t;
	typedef VertexArray::index_t index_t;

	typedef boost::function< float (float, float, float) > callback_t;
	SphericalROAM( 
		size_t nvertices, size_t ntriangles, 
		callback_t height_map );

	void dynamic_update( 
		vertex_t* vertices, color_t* colors, index_t* indices,
		const Vector3f& pos, const Vector3f& look );

	std::map< size_t, size_t > batch_data;
	size_t update;

	size_t nvertices, nindices;
	void set_offsets( size_t nvertices, size_t nindices );

	vertex_t* vertices()		{ return array.vertices; }
	color_t* colors()			{ return array.colors; }
	index_t* indices()			{ return array.indices; }

private:
	callback_t height_map;
};

