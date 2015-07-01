
#include <boost/python.hpp>
#include "cfd.hpp"

BOOST_PYTHON_MODULE(cfd)
{
	using namespace boost::python;
	class_< SimData >( "SimData" )
		.def( "p", &SimData::p )
		.def( "u", &SimData::u )
		.def( "v", &SimData::v )
		;

	class_< Simulation >( "Simulation", init<size_t>() )
		.def( "step", &Simulation::step )
		.def( "apply_boundary", &Simulation::apply_boundary )
		.property( "all_data", range( 
					&Simulation::data_begin, &Simulation::data_end ) )
		;
}

