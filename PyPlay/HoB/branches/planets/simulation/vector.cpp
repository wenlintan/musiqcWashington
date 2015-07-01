
#include "vector.hpp"

#include <string>
#include <boost/python.hpp>
#include <boost/python/object.hpp>
using namespace boost::python;

template< unsigned N, typename T >
struct vector_from_list {
	vector_from_list() {
		converter::registry::push_back(
			&convertible,
			&construct,
			type_id< Vector<N, T> >() );
	}

	static void* convertible( PyObject* obj_ptr ) {
		if( !PyList_Check( obj_ptr ) || PyList_Size( obj_ptr ) != N )
			return 0;
		return obj_ptr;
	}

	static void construct( PyObject* obj_ptr,
		converter::rvalue_from_python_stage1_data* data ) {

		void* storage = (
			(converter::rvalue_from_python_storage< 
			 	Vector<N, T> >*)data)->storage.bytes;

		boost::python::object pyobj( handle<>(borrowed(obj_ptr)) );
		new (storage) Vector<N, T>();

		Vector< N, T >& v = *((Vector<N, T>*)storage);
		for( unsigned i = 0; i < N; ++i )
			v[i] = extract<T>(pyobj[i]);
		data->convertible = storage;
	}
};

template< typename T >
void vector_set_item( Vector<3, T>& vec, unsigned i, T val ) {
	vec[i] = val;
}

template< size_t N, typename T >
class_< Vector<N, T> >& wrap_subtype( const std::string& name ) {
	typedef T (Vector<N, T>::*index_type)(unsigned) const;
	index_type index = &Vector<N, T>::index;

	vector_from_list<N, T>();
	return class_< Vector< N, T > >( name.c_str() )
		.def( "__getitem__", index )
		.def( "__setitem__", &vector_set_item<T> )

		.def( -self )
		//.def( self += self )
		.def( self + self )
		//.def( self -= self )
		.def( self - self )
		.def( self < self )

		.def( self * T() )
		.def( self *= T() )
		.def( self / T() )
		.def( self /= T() )

		.def( boost::python::self_ns::str(self) )
		.def( "length", &Vector<N, T>::length )
		.def( "length_sq", &Vector<N, T>::length_sq )
		.def( "dot", &Vector<N, T>::dot )
		.def( "cross", &Vector<N, T>::cross )
		;
}

void wrap_vector() {
	wrap_subtype< 2, float >( "Vector2f" )
		.def( init<float, float>() )
		.def( init<Vector<2, float> >() )
		;

	wrap_subtype< 3, float >( "Vector3f" )
		.def( init<float, float, float>() )
		.def( init<Vector<3, float> >() )
		;

	wrap_subtype< 4, unsigned char >( "Vector4ub" )
		.def( init<unsigned char, unsigned char, 
			unsigned char, unsigned char >() )
		.def( init<Vector<4, unsigned char> >() )
		;
}

