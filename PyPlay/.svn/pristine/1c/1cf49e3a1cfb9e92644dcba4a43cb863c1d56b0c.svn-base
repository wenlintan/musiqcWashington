
#include <map>

#include <boost/python.hpp>
#include <boost/function.hpp>
#include <boost/lambda/lambda.hpp>

#include <boost/functional/value_factory.hpp>
#include <boost/preprocessor/repetition/enum_params.hpp>

using namespace boost::python;

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

template< typename K, typename V >
void export_map( const std::string& n, const std::map< K, V >& m ) {
	typedef std::map< K, V > map;
	typedef map_item< K, V > wrap_map;

	class_< map >( n.c_str() )
		.def("__len__", &map::size)
		.def("__getitem__", &wrap_map().get, 
				return_value_policy<copy_non_const_reference>() )
		.def("__setitem__", &wrap_map().set)
		.def("__delitem__", &wrap_map().del)
		.def("clear", &map::clear)
		.def("__contains__", &wrap_map().in)
		.def("has_key", &wrap_map().in)
		.def("keys", &wrap_map().keys)
		.def("values", &wrap_map().values)
		.def("items", &wrap_map().items)
		.def("iteritems", &wrap_map().iteritems)
		;

}


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


