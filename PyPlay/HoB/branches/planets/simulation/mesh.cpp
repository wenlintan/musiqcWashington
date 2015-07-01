
#include <boost/python.hpp>
#include "mesh.hpp"

using namespace boost::python;
void wrap_mesh() {
	enum_< MeshVertexData::AttributeType >( "MeshAttributeType" )
		.value( "VERTEX", MeshVertexData::VERTEX )
		.value( "NORMAL", MeshVertexData::NORMAL )
		.value( "TEX_COORD0", MeshVertexData::TEX_COORD0 )
		.value( "COLOR", MeshVertexData::COLOR )
		;

	Vector2f (MeshVertexData::*get_v2f)( const size_t i ) =
		&MeshVertexData::get<2, float>;
	Vector3f (MeshVertexData::*get_v3f)( const size_t i ) = 
		&MeshVertexData::get<3, float>;
	Vector4ub (MeshVertexData::*get_v4ub)( const size_t i ) = 
		&MeshVertexData::get<4, unsigned char>;

	void (MeshVertexData::*set_v2f)( const size_t i, const Vector2f& v ) =
		&MeshVertexData::set<2, float>;
	void (MeshVertexData::*set_v3f)( const size_t i, const Vector3f& v ) =
		&MeshVertexData::set<3, float>;
	void (MeshVertexData::*set_v4ub)( const size_t i, const Vector4ub& v ) =
		&MeshVertexData::set<4, unsigned char>;

	class_< MeshVertexData, boost::noncopyable >( "MeshVertexData", no_init )
		.def( "__getitem__", get_v2f )
		.def( "__getitem__", get_v3f )
		.def( "__getitem__", get_v4ub )
		.def( "__setitem__", set_v2f )
		.def( "__setitem__", set_v3f )
		.def( "__setitem__", set_v4ub )
		;

	class_< Mesh, Mesh::pointer_type, bases<Component>,
		boost::noncopyable >( "Mesh", init< const std::string&, float >() )
		.def( "__getitem__", &Mesh::get_vertex_data,
			return_internal_reference<1>()	)
		;

	class_< BasicMesh, BasicMesh::pointer_type, bases<Mesh>,
		boost::noncopyable >( "BasicMesh", no_init )
		;

	class_< QuadMesh, QuadMesh::pointer_type, bases<BasicMesh>,
		boost::noncopyable >( "QuadMesh",
		init<const Vector3f&, const Vector2f&>() )
		.def( init<const Vector3f&, const Vector2f&,
			const MeshVertexData::AttributeType >() );
		;

	class_< CubeMesh, CubeMesh::pointer_type, bases<BasicMesh>,
		boost::noncopyable >( "CubeMesh",
		init<const Vector3f&, const Vector3f&>() )
		.def( init<const Vector3f&, const Vector3f&,
			const MeshVertexData::AttributeType >() );
		;

	class_< BatchMesh, BatchMesh::pointer_type, bases<Mesh>,
		boost::noncopyable >( "BatchMesh",
		init<Mesh&, const Vector3f&, const Vector3f&, 
			const size_t, const size_t>() )
		;

}

#include <boost/property_tree/xml_parser.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/foreach.hpp>

#include <map>

typedef std::map< std::string, std::vector<float> > sources_type;
sources_type load_sources( boost::property_tree::ptree& pt ) {
	using boost::property_tree::ptree;
	typedef ptree::const_assoc_iterator citer;
	sources_type result;

	std::pair< citer, citer > sources = pt.equal_range( "source" );
	for( citer& i = sources.first; i != sources.second; ++i ) {
		const std::string& id = i->second.get_child( "<xmlattr>.id" ).data();
		const ptree& arr = i->second.get_child( "float_array" );

		size_t count = arr.get<size_t>( "<xmlattr>.count" );
		std::cout << "Loading " << count << " from " << id << std::endl;
		result[ id ].reserve( count );

		std::stringstream ss( arr.data() );
		for( size_t f = 0; f < count; ++f ) {
			float val;
			ss >> val;
			result[ id ].push_back( val );
		}
	}

	return result;
}

struct Input {
	std::string semantic, source;
	float* data;
	size_t offset;
};

typedef std::vector< Input > inputs_type;
inputs_type load_inputs( boost::property_tree::ptree& pt ) {
	using boost::property_tree::ptree;
	typedef ptree::const_assoc_iterator citer;
	inputs_type result;

	std::pair< citer, citer > inputs = pt.equal_range( "input" );
	for( citer& i = inputs.first; i != inputs.second; ++i ) {
		const ptree& input = i->second;
		result.push_back( Input() );

		result.back().semantic = 
			input.get_child( "<xmlattr>.semantic" ).data();
		result.back().source =
			input.get_child( "<xmlattr>.source" ).data();

		result.back().offset = input.get<size_t>( "<xmlattr>.offset", 0 );
		std::cout << result.back().semantic << " from " << 
			result.back().source << " at " <<
			result.back().offset << std::endl;
	}

	return result;
}

struct IntegerPointerListCompare {
	size_t l;
	IntegerPointerListCompare( size_t l_ ): l( l_ )
	{}

	bool operator()( const size_t* lhs, const size_t* rhs ) const {
		for( size_t i = 0; i < l; ++i ) {
			if( lhs[i] < rhs[i] ) return true;
			else if( lhs[i] > rhs[i] )	return false;
		}
		return false;
	}
};


Mesh::Mesh( const std::string& filename, float scale ): 
	Component( Component::Mesh ) {

	using boost::property_tree::ptree;
	boost::property_tree::ptree pt;
	
	std::ifstream infile( filename.c_str() );
	boost::property_tree::read_xml( infile, pt );

	ptree& mesh =  pt.get_child( "COLLADA.library_geometries.geometry.mesh" ); 
	sources_type sources = load_sources( mesh );
	inputs_type vinputs = load_inputs( mesh.get_child( "vertices" ) );

	ptree& polylist = mesh.get_child( "polylist" );
	size_t pcount = polylist.get<size_t>( "<xmlattr>.count" );
	inputs_type inputs = load_inputs( polylist );

	std::cout << "Mapping vertex inputs." << std::endl;
	Input vert_input;
	for( inputs_type::iterator i = inputs.begin(); i != inputs.end(); ++i )
		if( i->semantic == "VERTEX" ) {
			vert_input = *i;
			inputs.erase( i );
			break;
		}

	for( inputs_type::iterator i = vinputs.begin();
		i != vinputs.end(); 
		++i ) {

		inputs.push_back( *i );
		inputs.back().offset = vert_input.offset;
	}

	std::vector< size_t > vcounts;
	vcounts.reserve( pcount );
	std::stringstream raw_vcounts( polylist.get_child( "vcount" ).data() );
	size_t npoints = 0, nindices = 0;

	std::cout << "Loading vcounts." << std::endl;
	for( size_t p = 0; p < pcount; ++p ) {
		size_t val;
		raw_vcounts >> val;
		vcounts.push_back( val );

		npoints += val;
		if( val == 3 ) nindices += 3;
		else if( val == 4 ) nindices += 6;
	}

	typedef std::map< size_t*, size_t, IntegerPointerListCompare > 
		vert_map_type;
	vert_map_type verts( IntegerPointerListCompare( inputs.size() ) );
	size_t nverts = 0;

	std::vector< size_t > p;
	p.reserve( npoints * inputs.size() );
	std::stringstream raw_p( polylist.get_child( "p" ).data() );

	std::cout << "Loading p data." << std::endl;
	std::cout << npoints << std::endl;
	for( size_t i = 0; i < npoints * inputs.size(); ++i ) {
		size_t val;
		raw_p >> val;
		p.push_back( val );

		if( i % inputs.size() == inputs.size()-1 )
			if( !verts.count( &p[ i - inputs.size() + 1 ] ) )
				verts[ &p[ i - inputs.size() + 1 ] ] = nverts++;
	}

	std::vector< MeshVertexData > vdata;
	for( inputs_type::iterator i = inputs.begin(); i != inputs.end(); ++i ){
		MeshVertexData::AttributeType attr;
		if( i->semantic == "POSITION" )		attr = MeshVertexData::VERTEX;
		else if( i->semantic == "NORMAL" )	attr = MeshVertexData::NORMAL;

		MeshVertexData ndata = { attr, MeshVertexData::FLOAT, 3, 0, 0, 0 };
		vdata.push_back( ndata );

		if( sources.count( i->source.substr(1) ) )
			i->data = &sources[ i->source.substr(1) ][0];
		else
			std::cout << "Failed to match source " << i->source << std::endl;
	}

	std::cout << "Allocating and writing data." << std::endl;
	float* data = (float*)allocate_data( verts.size(), vdata );
	for( vert_map_type::iterator i = verts.begin(); 
		i != verts.end(); 
		++i ) {

		size_t* ind = i->first;
		float* d = data + 3 * inputs.size() * i->second;

		for( inputs_type::iterator iter = inputs.begin(); 
			iter != inputs.end();
			++iter ) {
			
			float s = ( iter->semantic == "POSITION" )? scale: 1.0f;
			for( size_t j = 0; j < 3; ++j )
				d[ j ] = iter->data[ ind[ iter->offset ] * 3 + j ] * s;
			d += 3;
		}
	}

	std::cout << "Allocating and writing index data." << std::endl;
	unsigned short* index = (unsigned short*)
		allocate_index_data< unsigned short >( nindices );
	unsigned short* i = index;

	size_t* p_iter = &p[0];
	for( size_t p = 0; p < pcount; ++p ) {
		if( vcounts[p] == 3 ) {
			*i++ = (unsigned short)verts[ p_iter ];
			p_iter += inputs.size();
			*i++ = (unsigned short)verts[ p_iter ];
			p_iter += inputs.size();
			*i++ = (unsigned short)verts[ p_iter ];
			p_iter += inputs.size();
		} else if( vcounts[p] == 4 ) {
			unsigned short i1 = (unsigned short)verts[ p_iter ];
			unsigned short i2 = (unsigned short)verts[ p_iter + inputs.size() ];
			unsigned short i3 = (unsigned short)verts[ p_iter + 2*inputs.size() ];
			unsigned short i4 = (unsigned short)verts[ p_iter + 3*inputs.size() ];
			p_iter += 4*inputs.size();

			*i++ = i1;	*i++ = i2;	*i++ = i3;
			*i++ = i1;	*i++ = i3;	*i++ = i4;
		} else {
			p_iter += vcounts[p]*inputs.size();
		}

	}
}

size_t BasicMesh::vdata_from_attributes( 
	const MeshVertexData::AttributeType type,
	std::vector< MeshVertexData >& vdata ) {

	size_t nbytes_per_vert = 0;
	if( type & MeshVertexData::VERTEX ) {
		MeshVertexData d = { MeshVertexData::VERTEX, MeshVertexData::FLOAT, 3 };
		vdata.push_back( d );
		nbytes_per_vert += sizeof(float)*3;
	}

	if( type & MeshVertexData::NORMAL ) {
		MeshVertexData d = { MeshVertexData::NORMAL, MeshVertexData::FLOAT, 3 };
		vdata.push_back( d );
		nbytes_per_vert += sizeof(float)*3;
	}

	if( type & MeshVertexData::TEX_COORD0 ) {
		MeshVertexData d = { MeshVertexData::TEX_COORD0, 
			MeshVertexData::FLOAT, 2 };
		vdata.push_back( d );
		nbytes_per_vert += sizeof(float)*2;
	}

	if( type & MeshVertexData::COLOR ) {
		MeshVertexData d = { MeshVertexData::COLOR,
			MeshVertexData::UCHAR, 4 };
		vdata.push_back( d );
		nbytes_per_vert += 4;
	}

	return nbytes_per_vert;
}

QuadMesh::QuadMesh( const Vector3f& pos, const Vector2f& dim,
	const MeshVertexData::AttributeType type ) {

	size_t nvertices = 4, nindices = 6;
	std::vector< MeshVertexData > vdata;

	size_t nbytes_per_vert = vdata_from_attributes( type, vdata );
	unsigned char* data = (unsigned char*)allocate_data( nvertices, vdata );
	unsigned short* indices = (unsigned short*)
		allocate_index_data<unsigned short>(nindices);

	Vector3f off[2];
	for( unsigned i = 0; i < 2; ++i )		off[i].index(i) = dim.index(i);

	unsigned char* p = data;
	if( type & MeshVertexData::VERTEX ) {
		write_vector( pos, (float*)(p+0) );
		write_vector( pos + off[0], (float*)(p+1*nbytes_per_vert) );
		write_vector( pos + off[0] + off[1], (float*)(p+2*nbytes_per_vert));
		write_vector( pos + off[1], (float*)(p+3*nbytes_per_vert) );
		p += sizeof(float)*3;
	}

	if( type& MeshVertexData::TEX_COORD0 ) {
		write_vector( Vector2f(), (float*)(p+0) );
		write_vector( Vector2f(1., 0.), (float*)(p+1*nbytes_per_vert) );
		write_vector( Vector2f(1., 1.), (float*)(p+2*nbytes_per_vert) );
		write_vector( Vector2f(0., 1.), (float*)(p+3*nbytes_per_vert) );
		p += sizeof(float)*2;
	}

	indices[0] = 0;		indices[1] = 1;		indices[2] = 2;
	indices[3] = 0;		indices[4] = 2;		indices[5] = 3;
}

CubeMesh::CubeMesh( const Vector3f& pos, const Vector3f& dim,
	const MeshVertexData::AttributeType type ) {

	size_t nvertices = 24, nindices = 36;
	std::vector< MeshVertexData > vdata;

	size_t nfloats_per_vert = vdata_from_attributes( type, vdata );
	float* data = (float*)allocate_data( nvertices, vdata );
	unsigned short* indices = (unsigned short*)
		allocate_index_data<unsigned short>(nindices);

	Vector3f off[3];
	for( unsigned i = 0; i < 3; ++i )		off[i].index(i) = dim.index(i);

	float* p = data;
	for( unsigned i = 0; i < 3; ++i ) {
		unsigned j = (i+4)%3, k = (i+5)%3;
		if( type & MeshVertexData::VERTEX ) {
			write_vector( pos, p+0 );
			write_vector( pos+off[k], p+1*nfloats_per_vert );
			write_vector( pos+off[j]+off[k], p+2*nfloats_per_vert );
			write_vector( pos+off[j], p+3*nfloats_per_vert );

			write_vector( pos+off[0]+off[1]+off[2], p+4*nfloats_per_vert );
			write_vector( pos+off[j], p+5*nfloats_per_vert );
			write_vector( pos+off[j]+off[k], p+6*nfloats_per_vert );
			write_vector( pos+off[k], p+7*nfloats_per_vert );
			p += 3;
		}
		
		if( type & MeshVertexData::NORMAL ) {
			Vector3f n = off[i] / off[i].index(i);
			write_vector( n, p+0*nfloats_per_vert );
			write_vector( n, p+1*nfloats_per_vert );
			write_vector( n, p+2*nfloats_per_vert );
			write_vector( n, p+3*nfloats_per_vert );

			n = -n;
			write_vector( n, p+4*nfloats_per_vert );
			write_vector( n, p+5*nfloats_per_vert );
			write_vector( n, p+6*nfloats_per_vert );
			write_vector( n, p+7*nfloats_per_vert );
			p += 3;
		}

		if( type & MeshVertexData::TEX_COORD0 ) {
			for( unsigned l = 0; l < 8; ++l )
				write_vector( Vector2f( 0., 0. ), p+l*nfloats_per_vert );
			p += 2;
		}

		p += 7*nfloats_per_vert;
	}

	for( unsigned short i = 0; i < 6; ++i ) {
		indices[0] = i*4;
		indices[1] = i*4 + 1;
		indices[2] = i*4 + 2;
		indices[3] = i*4;
		indices[4] = i*4 + 2;
		indices[5] = i*4 + 3;
		indices += 6;
	}
}

BatchMesh::BatchMesh( Mesh& mesh, const Vector3f& dx, const Vector3f& dy,
	const size_t nx, const size_t ny ) {

	const size_t n = nx * ny;
	std::vector< MeshVertexData > copy_data( mesh.begin(), mesh.end() );

	char* data = (char*)allocate_data( mesh.nvertices*n, copy_data );
	unsigned short* indices = (unsigned short*)
		allocate_index_data<unsigned short>( mesh.nindices*n );

	MeshVertexData vdata;
	for( std::vector< MeshVertexData >::iterator i = copy_data.begin();
		i != copy_data.end(); ++i ) {
		if( i->type == MeshVertexData::VERTEX )
			vdata = *i;
	}

	char* cur_data = data;
	unsigned short* cur_indices = indices;
	for( size_t y = 0; y < ny; ++y ) for( size_t x = 0; x < nx; ++x ) {
		std::memcpy( cur_data, mesh.data_buffer[0], 
			vdata.stride*mesh.nvertices );

		for( size_t v = 0; v < mesh.nvertices; ++v ) {
			float* pt_data = (float*)(cur_data + vdata.stride*v + vdata.offset);
			Vector3f pt = Vector3f( pt_data ) + dx*x + dy*y;
			for( unsigned char i = 0; i < 3; ++i )
				pt_data[ i ] = pt[ i ];
		}

		for( size_t i = 0; i < mesh.nindices; ++i ) {
			cur_indices[i] = ((unsigned short*)mesh.index_data.data)[i] +
				(unsigned short)((x*ny + y)*mesh.nvertices);
		}

		cur_data += vdata.stride*mesh.nvertices;
		cur_indices += mesh.nindices;
	}



}


