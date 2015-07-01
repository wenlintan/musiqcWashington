
#include <iostream>
#include <fstream>
#include <vector>

#include <gsl/gsl_multimin.h>

typedef std::pair< double, double > point_type;
point_type make_point( std::ifstream& f ) {
	point_type pt;
	f >> pt.first;
	f >> pt.second;
	return pt;
};

double interp_linear( double t, double a0, double a1 ) {
	return a0 + t*(a1-a0);
}

double interp_cubic( double t, double a0, double a1, double a2, double a3 ) {
	double temp[4];
	temp[0] = 2 * a1;
	temp[1] = -a0 + a2;
	temp[2] = 2*a0 - 5*a1 + 4*a2 - a3;
	temp[3] = -a0 + 3*a1 - 3*a2 + a3;
	
	return 0.5 * (temp[0] + t*temp[1] + t*t*temp[2] + t*t*t*temp[3]);
}

std::vector< point_type > sim_data, data;
double fit_error( const gsl_vector* v, void* params ) {
	double err = 0.;
	double b = gsl_vector_get( v, 0 ), m = gsl_vector_get( v, 1 );
	if( b < 0. || m < 0. ) return 100000.;

	for( size_t i = 0; i < data.size(); ++i ) {
		point_type pt = data[i];
		double x = m*pt.first + b, simy;
		if( x < sim_data.front().first )
			simy = interp_linear( x / sim_data.front().first, 
				1.0, sim_data.front().second );
		else if( x >= sim_data.back().first )
			//simy = interp_linear( (x - sim_data.back().first) / 1000, 
			//	sim_data.back().second, 0. );
			simy = sim_data.back().second;
		else {
			std::vector< point_type >::iterator iter = sim_data.begin();
			while( iter->first < x ) ++iter;

			--iter;
			double prevx = iter->first, prevy = iter->second;
			++iter;

			simy = interp_linear( (x - prevx) / 
					(iter->first - prevx),
				prevy, iter->second );
		}

		err += (pt.second - simy)*( pt.second - simy );
	}

	std::cout << m << ", " << b << ", " <<err << std::endl;
	return err;
}

int main( int argc, char** argv ) {

	if( argc < 3 ) {
		std::cout << "usage: " << argv[0] << 
			" <simulation> <data>" << std::endl;
		exit( 0 );
	}

	std::ifstream sim_file( argv[1] );
	size_t nlines = 0;
	sim_file >> nlines;
	for( size_t i = 0; i < nlines; ++i ) {
		sim_data.push_back( make_point( sim_file ) );
		sim_data.back().first = 0.5*138*1.66e-27*
			sim_data.back().first * sim_data.back().first / 1.38e-23;
		sim_data.back().second = 1. - sim_data.back().second;
		std::cout << "Sim: " << sim_data.back().first << ", " <<
			sim_data.back().second << std::endl;
	}

	std::ifstream data_file( argv[2] );
	data_file >> nlines;
	for( size_t i = 0; i < nlines; ++i ) {
		data.push_back( make_point( data_file ) );
		double npoints = 0;
		data_file >> npoints;
		std::cout << "Data: " << data.back().first << ", " <<
			data.back().second << std::endl;
	}

	gsl_vector* fit = gsl_vector_alloc( 2 );
	gsl_vector_set( fit, 0, 0.5 );
	gsl_vector_set( fit, 1, 8e-4 );

	gsl_vector* step_size = gsl_vector_alloc( 2 );
	gsl_vector_set( step_size, 0, 0.2 );
	gsl_vector_set( step_size, 1, 1e-4 );

	gsl_multimin_function fn;
	fn.n = 2;
	fn.f = fit_error;
	fn.params = 0;
	
	const gsl_multimin_fminimizer_type *T =
		gsl_multimin_fminimizer_nmsimplex2;
	gsl_multimin_fminimizer *s = gsl_multimin_fminimizer_alloc( T, 2 );
	gsl_multimin_fminimizer_set( s, &fn, fit, step_size );	

	int status = 0;
	size_t iter = 0;
	do {
		status = gsl_multimin_fminimizer_iterate( s );
		if( status ) break;

		double size = gsl_multimin_fminimizer_size( s );
		status = gsl_multimin_test_size( size, 1e-6 );
	} while( status == GSL_CONTINUE && ++iter < 100000 );

	std::cout << "Converged at " << iter << " iterations." << std::endl;
	std::cout << "Intercept: " << gsl_vector_get( s->x, 0 ) << std::endl;
	std::cout << "Rate: " << gsl_vector_get( s->x, 1 ) << std::endl;


	gsl_vector_free( fit );
	gsl_vector_free( step_size );
	gsl_multimin_fminimizer_free( s );
	return 0;
}

