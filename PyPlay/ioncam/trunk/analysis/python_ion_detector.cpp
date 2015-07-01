
#include <boost/python/detail/wrap_python.hpp>
#include <numpy/arrayobject.h>

#include <boost/python.hpp>
using namespace boost::python;

#include <iostream>
#include "ion_detector.hpp"

// From: http://code.google.com/p/numpy-boost/source/browse/trunk/include/numpy_boost.hpp
template<class T>
struct numpy_type_map {
    static const int typenum;
};

template<>
const int numpy_type_map<float>::typenum = NPY_FLOAT;

template<>
const int numpy_type_map<std::complex<float> >::typenum = NPY_CFLOAT;

template<>
const int numpy_type_map<double>::typenum = NPY_DOUBLE;

template<>
const int numpy_type_map<std::complex<double> >::typenum = NPY_CDOUBLE;

template<>
const int numpy_type_map<long double>::typenum = NPY_LONGDOUBLE;

template<>
const int numpy_type_map<std::complex<long double> >::typenum = NPY_CLONGDOUBLE;

template<>
const int numpy_type_map<boost::int8_t>::typenum = NPY_INT8;

template<>
const int numpy_type_map<boost::uint8_t>::typenum = NPY_UINT8;

template<>
const int numpy_type_map<boost::int16_t>::typenum = NPY_INT16;

template<>
const int numpy_type_map<boost::uint16_t>::typenum = NPY_UINT16;

template<>
const int numpy_type_map<boost::int32_t>::typenum = NPY_INT32;

template<>
const int numpy_type_map<boost::uint32_t>::typenum = NPY_UINT32;

template<>
const int numpy_type_map<boost::int64_t>::typenum = NPY_INT64;

template<>
const int numpy_type_map<boost::uint64_t>::typenum = NPY_UINT64;

template<class T>
struct numpy_boost_from_python
{
    static void* convertible(PyObject* obj_ptr) {
        PyArrayObject* a;
        
        // Try to get PyArrayObject with correct type and dimension 2
        a = (PyArrayObject*)PyArray_FromObject(obj_ptr, numpy_type_map<T>::typenum, 2, 2);
        if (a == NULL)  return 0;

        Py_DECREF(a);
        return obj_ptr;
    }

    static void construct( PyObject* obj_ptr,
            boost::python::converter::rvalue_from_python_stage1_data* data) {
            
        void* storage = (
            (boost::python::converter::rvalue_from_python_storage< Image<T> >*)
            data)->storage.bytes;

        // We've already checked that array is dimension 2
        PyArrayObject* a = (PyArrayObject*)PyArray_ContiguousFromAny(
            obj_ptr, numpy_type_map<T>::typenum, 2, 2);
        
        size_t h = *PyArray_DIMS(a), w =*(PyArray_DIMS(a)+1);
        typename Image<T>::extents_type exts( w, h );
        new (storage) Image< T >( exts, (T*)PyArray_DATA(a), (T*)PyArray_DATA(a)+w*h );
        
        Py_DECREF(a);
        data->convertible = storage;
   }

    numpy_boost_from_python()
    {
        boost::python::converter::registry::push_back(
            &convertible, &construct, boost::python::type_id< Image<T> >());
    }
};

struct ReleasePythonGIL {
    inline ReleasePythonGIL()   {   thread_state = PyEval_SaveThread(); }
    inline ~ReleasePythonGIL()  {   PyEval_RestoreThread( thread_state ); }
    
private:
    PyThreadState* thread_state;
};

list python_ion_detect( IonDetector* det, Image<float> data ) {
	list python_result;
    IonDetector::result_type result;
    
    {
        ReleasePythonGIL gil;
        result = (*det)( data );
    }

	for( size_t i = 0; i < result.size(); ++i )
		python_result.append( result[i] );
	return python_result;
}

BOOST_PYTHON_MODULE( analysis ) {
    import_array();
    numpy_boost_from_python< float > float_converter;
    
	class_< IonData >( "IonData", init< float, float, float >() )
		.def_readwrite( "x", &IonData::x )
		.def_readwrite( "y", &IonData::y )
		.def_readwrite( "r", &IonData::r )
		;

	class_< IonDetector >( "IonDetector" )
		.def_readwrite( "canny_threshold", &IonDetector::canny_threshold )
		.def_readwrite( "canny_continue_threshold", 
			&IonDetector::canny_continue_threshold )
		.def_readwrite( "hough_threshold", &IonDetector::hough_threshold )
        .def_readwrite( "blob_threshold", &IonDetector::blob_threshold )
		
		.def( "__call__", &python_ion_detect )
		;
}

