
#include <cmath>
#include <boost/numeric/ublas/matrix.hpp>
#include <boost/numeric/ublas/vector.hpp>
#include <boost/numeric/ublas/lu.hpp>

#include <boost/range/irange.hpp>

using namespace boost::numeric::ublas;

template< class T, class In >
bool invert( const matrix_expression<In>& input, matrix<T>& output ) {
	matrix<T> A(input);
	permutation_matrix<std::size_t> pm( A.size1() );	

	int res = lu_factorize( A, pm );
	if( res )	return false;

	output.assign( identity_matrix<T>( A.size1() ) );
	lu_substitute( A, pm, output );
	return true;
}

void pprint( matrix<float>& m ) {
	for( size_t i = 0; i < m.size1(); ++i ) {
		for( size_t j = 0; j < m.size2(); ++j )
			std::cout << m(i, j) << " ";
		std::cout << std::endl;
	}
}
template< class Function >
struct FitFunction {
	template< typename T >
	int operator()( matrix<T>& values, vector<T>& parameters ) {
		
		matrix_column< matrix<T> > x( values, 0 ), y( values, 1 );
		size_t iterations = 0;

		vector< T > estimate( x.size() ), temp( x.size() ); 
		matrix< T > inverse( Function::nparameters, Function::nparameters );
		matrix< T > design_matrix( x.size(), Function::nparameters );

		do {
			Function::values( x, parameters, estimate );
			Function::design_matrix( x, parameters, design_matrix );

			if( !invert<T>( prod( trans(design_matrix), 
				design_matrix ), inverse ) ) {

				return -1;
			}

			temp = prod( trans(design_matrix), y - estimate ); 
			parameters += prod( inverse, temp );
			++iterations;
		} while( iterations < 100 );

		return (int)iterations;
	}

	template< typename T >
	int operator()( 
		const vector<T>& values, vector<T>& parameters ) {

		vector< T > pos( values.size(), 0. );
		for( size_t i = 0; i < values.size(); ++i )
			pos(i) = (T)i;

		matrix< T > mat( values.size(), 2 );
		matrix_column< matrix<T> > x( mat, 0 );
		matrix_column< matrix<T> > y( mat, 1 );

		x = pos; y = values;
		return (*this)( mat, parameters );
	}
};

template< typename T >
class GaussianFunction {
	struct ValueFunctor {
		typedef T value_type;
		typedef T result_type;

		T mean, sigma, ampl, base;
		ValueFunctor( T mean_, T sigma_, T ampl_, T base_ ):
			mean( mean_ ), sigma( sigma_ ), ampl( ampl_ ), base( base_ )
		{}


		result_type operator()( const value_type& x ) {
			return base + ampl *
				std::exp( -(x-mean)*(x-mean) / 2 / sigma / sigma );
		}
	};

public:
	const static size_t nparameters = 4;

	template< typename E >
	static void values( const vector_expression<E>& pos, 
		const vector<T>& param, vector<T>& out ) {

		T mean = param(0), sigma = param(1), ampl = param(2), base = param(3);
		std::transform( pos().begin(), pos().end(), out.begin(), 
			 ValueFunctor( mean, sigma, ampl, base ) );
	}

	template< typename E1, typename E2 >
	static void design_matrix( const vector_expression<E1>& pos, 
		const vector<E2>& param, matrix<T>& out ) {

		T mean = param(0), sigma = param(1), ampl = param(2);
		for( size_t i = 0; i < out.size1(); ++i ) {
			matrix_row< matrix<T> > row( out, i );
			T x = pos()( i );

			T diff = (x - mean);
			T s2 = 1. / 2 / sigma / sigma;
			T val = ampl * std::exp( -diff*diff * s2 );

			row( 0 ) = 2 * diff * s2 * val;
			row( 1 ) = 2 * diff * diff * s2 / sigma * val;
			row( 2 ) = val / ampl;
			row( 3 ) = 1.; 
		}
	}
};



