
#pragma once

#include <boost/utility/enable_if.hpp>
#include <boost/mpl/vector.hpp>
#include <boost/mpl/pop_front.hpp>

#include <vector>
#include <algorithm>

#include "component.hpp"
#include "vector.hpp"

void wrap_mesh();

struct MeshVertexData {
	enum AttributeDataType { FLOAT, UINT, UCHAR, USHORT };
	enum AttributeType { VERTEX=1, NORMAL=2, TEX_COORD0=4, COLOR=8,
		USER = 100, LAST_USER=16000 };

	template< AttributeType atype >
	struct Attribute {
		const static AttributeType type = atype;
	};

	template< typename T >
	struct Data {};
	
	template<> struct Data< float >{ 
		const static AttributeDataType value = FLOAT;
		const static size_t ncomponents = 1;
	};

	template<size_t N> struct Data< float[N] >{ 
		const static AttributeDataType value = FLOAT;
		const static size_t ncomponents = N;
	};

	template<> struct Data< unsigned int >{
		const static AttributeDataType value = UINT;
		const static size_t ncomponents = 1;
	};

	template<> struct Data< unsigned short >{
		const static AttributeDataType value = USHORT;
		const static size_t ncomponents = 1;
	};

	template<> struct Data< unsigned char >{
		const static AttributeDataType value = UCHAR;
		const static size_t ncomponents = 1;
	};

	template<size_t N> struct Data< unsigned char[N] >{
		const static AttributeDataType value = UCHAR;
		const static size_t ncomponents = N;
	};

	template< typename T >
	T get( const size_t index ) {
		assert( Data<T>::value == type && Data<T>::ncomponents == 1 );
		return *(T*)( data + offset + stride*index );
	}

	template< size_t N, typename T >
	Vector< N, T > get( const size_t index ) {
		assert( Data<T>::value == type && N == ncomponents );
		return Vector< N, T >( (T*)(data + offset + stride*index ) );
	}

	template< typename T >
	void set( const size_t index, const T t ) {
		assert( Data<T>::value == type && Data<T>::ncomponents == 1 );
		*(T*)( data + offset + stride*index ) = t;
	}

	template< size_t N, typename T >
	void set( const size_t index, const Vector<N, T>& v ) {
		assert( Data<T>::value == data_type && N == ncomponents );
		std::memcpy( data + offset + stride*index, v.d, sizeof(T)*N );
	}

	AttributeType 		type;
	AttributeDataType 	data_type;
	size_t 				ncomponents;

	size_t			stride, offset;
	unsigned char*	data;
};

struct MeshIndexData {
	MeshVertexData::AttributeDataType	type;
	unsigned char*		data;
};

struct Mesh: Component {
	typedef boost::shared_ptr< Mesh > pointer_type;
	typedef std::vector<MeshVertexData> vertex_data_type;
	typedef vertex_data_type::iterator iterator_type;

	Mesh( const std::string& filename, float scale = 1.0f );
	Mesh(): Component( Component::Mesh )
	{}

	~Mesh() {
		std::vector<unsigned char*>::iterator i;
		for( i = data_buffer.begin(); i != data_buffer.end(); ++i )
			delete [] *i;
	}

	template<typename T, typename Enable = void>
	struct AllocSize {};

	template<typename Map>
	struct AllocSize<Map, 
		typename boost::enable_if< boost::mpl::empty<Map> >::type> {
		const static size_t value = 0;
	};

	template<typename Map>
	struct AllocSize<Map, 
		typename boost::disable_if< boost::mpl::empty<Map> >::type> {
		typedef typename boost::mpl::front< Map >::type front_type;
		typedef typename boost::mpl::pop_front< Map >::type remainder_type;

		const static size_t value = sizeof( front_type::second )
			+ AllocSize< remainder_type >::value;
	};

	template<typename Map, typename Enable = void>
	struct BindAttributes {};

	template<typename Map>
	struct BindAttributes<Map, 
		typename boost::enable_if< boost::mpl::empty<Map> >::type> {
		static void bind( vertex_data_type& vertex_data,
			unsigned char* data, size_t stride, size_t offset=0) {}
	};

	template<typename Map>
	struct BindAttributes<Map, 
		typename boost::disable_if< boost::mpl::empty<Map> >::type> {
		typedef typename boost::mpl::front< Map >::type front_type;
		typedef typename boost::mpl::pop_front< Map >::type remainder_type;

		static void bind(vertex_data_type& vertex_data,
			unsigned char* data, size_t stride, size_t offset=0) {
			MeshVertexData new_data = { 
				front_type::first::type,
				MeshVertexData::Data< front_type::second >::value,
				MeshVertexData::Data< front_type::second >::ncomponents,
				stride, offset, data };

			vertex_data.push_back( new_data );
			offset += sizeof( front_type::second );
			BindAttributes< remainder_type >::bind( 
				vertex_data, data, stride, offset );
		}
	};

	template< typename T >
	void* allocate_data( size_t ncomponents, T* type=0 ) {
		size_t size = AllocSize<T>::value;
		data_buffer.push_back( new unsigned char[size*ncomponents] );
		BindAttributes<T>::bind( vertex_data, data_buffer.back(), size );
		nvertices = ncomponents;
		return data_buffer.back();
	}

	void* allocate_data( size_t nvertices_, vertex_data_type data ) {
		size_t s = 0;
		for( iterator_type i = data.begin(); i != data.end(); ++i ) {
			size_t dsize = 0;
			switch( i->data_type ) {
				case MeshVertexData::FLOAT:		dsize = sizeof(float); break;
				case MeshVertexData::UINT:		dsize = sizeof(int); break;
				case MeshVertexData::USHORT:	dsize = sizeof(short); break;
				case MeshVertexData::UCHAR:		dsize = sizeof(char); break;
				default:
					break;
			}

			i->offset = s;
			s += dsize * i->ncomponents;
		}

		data_buffer.push_back( new unsigned char[ nvertices_*s ] );
		for( iterator_type i = data.begin(); i != data.end(); ++i ) {
			i->stride = s;
			i->data = data_buffer.back();
			vertex_data.push_back( *i );
		}

		nvertices = nvertices_;
		return data_buffer.back();
	}

	template< typename T >
	void* allocate_index_data( size_t ncomponents, T* type=0 ) {
		data_buffer.push_back( new unsigned char[sizeof(T)*ncomponents] );
		MeshIndexData index = { 
			MeshVertexData::Data<T>::value, 
			data_buffer.back() };
		index_data = index;
		nindices = ncomponents;
		return data_buffer.back();
	}

	iterator_type begin()	{ return vertex_data.begin(); }
	iterator_type end()		{ return vertex_data.end(); }
	MeshIndexData& index()	{ return index_data; }

	MeshVertexData& get_vertex_data( MeshVertexData::AttributeType t ) {
		for( iterator_type i = begin(); i != end(); ++i )
			if( i->type == t ) return *i;
		assert( 0 && "Bad vertex data." );
	}

	std::vector<unsigned char*>		data_buffer;
	size_t 							nvertices, nindices;

	vertex_data_type		vertex_data;
	MeshIndexData			index_data;
};

struct BasicMesh: Mesh {
	typedef boost::shared_ptr<BasicMesh> pointer_type;

protected:
	size_t vdata_from_attributes(
		const MeshVertexData::AttributeType t,
		std::vector<MeshVertexData>& vdata );

	template< size_t N >
	void write_vector( const Vector<N, float>& v, float* p ) {
		for( unsigned i = 0; i < N; ++i )
			p[i] = v.index( i );
	}
};

struct QuadMesh: BasicMesh {
	typedef boost::shared_ptr<QuadMesh> pointer_type;
	QuadMesh( const Vector3f& pos, const Vector2f& dim,
		const MeshVertexData::AttributeType t = MeshVertexData::VERTEX );
};

struct CubeMesh: BasicMesh {
	typedef boost::shared_ptr<CubeMesh> pointer_type;
	CubeMesh( const Vector3f& pos, const Vector3f& dim, 
	   const MeshVertexData::AttributeType t = MeshVertexData::VERTEX );

};

struct BatchMesh: Mesh {
	typedef boost::shared_ptr<BatchMesh> pointer_type;
	BatchMesh( Mesh& base_mesh, const Vector3f& xoff, const Vector3f& yoff,
		const size_t sizex, const size_t sizey );

};

