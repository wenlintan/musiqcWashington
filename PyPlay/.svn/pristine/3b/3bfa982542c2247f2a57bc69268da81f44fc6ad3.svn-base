
#include <iostream>
#include <fstream>
#include <complex>
#include <vector>

#include <boost/array.hpp>

#include <boost/numeric/odeint.hpp>

using namespace std;
using namespace boost::numeric::odeint;

const double pi = 3.141592654;
const double hbar = 6.62e-34 / 2 / pi;
const double kb = 1.38e-23;

const double Lambda = 2 * pi * 1. / 8e-9;
const double Omega = 2 * pi * 1. / 10e-9;
const double Delta = -Lambda / 2.0;
double s = 0.9; // 2 * (Omega / Lambda)*(Omega / Lambda);

const double kz = 0.7 * 2 * pi / 493e-9;
const double m = 138 * 1.67e-27;

const double E0 = hbar * Lambda / 2 * sqrt( 1 + s );
const double t0 = 1.0 / ( Lambda * s / 2 / (1 + s) );
const double r = (hbar * kz) * (hbar * kz) / 2 / m / E0;
double delta = -0.8; // hbar * Delta / E0;

struct HeatingRate {

	typedef complex<double> complex_type;
	typedef boost::array< double, 1 > state_type;

	double ebar, delta, s, dt, endt;
	std::vector< double > energies;

	HeatingRate( double ebar_, double delta_, double s_ = 0.9,
		double dt_ = 1.0e-4, double endt_ = 0.1 ): 
		ebar( ebar_ ), delta( delta_ ), s( s_ ), dt( dt_ ), endt( endt_ )
	{}

	void integrate() {
		state_type starte = {{ ebar * 3.0 }};
		boost::function< void (const state_type& e, const double t) > cb =
			boost::bind( &HeatingRate::store_data, boost::ref(*this), _1, _2 );

		integrate_const( 
			make_dense_output( 1.0e-6, 1.0e-6,
				runge_kutta_dopri5< state_type >() ),
			*this, starte, 0., endt, dt, cb );
	}

	double dndt_th( const size_t t ) {
		size_t t_off = 0;
		double result = 0.0;

		double d = 1.0e4;
		while( energies[t_off] > 0.0 ) {
			d = dndt( energies[ t + t_off ] );
			d *= 2.0 * exp( -energies[ t_off ] / ebar );
			
			double de = energies[ t_off+1 ] - energies[ t_off ];
			d *= sinh( fabs( de ) / 2.0 / ebar );
			result += d;
			++t_off;
		}
		return result;	
	}

	void output( std::ostream& out ) {
		for( size_t i = 0; i < energies.size(); ++i ) {
			out << i*dt << '\t' << dndt_th( i ) << endl;
		}
	}

	complex_type Z( const double epsilon ) {
		if( epsilon < 1.0e-10 / r )
			return complex_type( 0.0, 1.0 / (delta*delta + 1.0) );

		complex_type cd( delta, 1.0 );
		return 1.0 / 2.0 / sqrt( epsilon * r ) *
			complex_type( 0, 1.0 ) /
			sqrt( 1.0 - cd * cd / 4.0 / epsilon / r ); 
	}

	double dedt( const double epsilon ) {
		complex_type z = Z( epsilon );
		return ( z.real() + delta * z.imag() ) / t0;
	}

	double dndt( const double epsilon ) {
		return Z( epsilon ).imag(); // / t0;
	}

	void operator ()( const state_type& e, state_type& dedt, double t ) {
		dedt[0] = HeatingRate::dedt( e[0] );
	}

	void store_data( const state_type& e, const double t ) {
		energies.push_back( e[0] );
	}
};

int main( int argc, char** argv ) {
	if( argc < 3 ) {
		cout << "usage: " << argv[0] << " data_file output_file" << endl;
		return 0;
	}

	typedef boost::array< double, 3 > state_type;
	state_type params = {{10.0 / r, -0.8, 1.0 / 300.0 }};
	state_type dparams = {{ 1.0 / r, 0.05, 1.0e-4 }};
	double cur_err = 1.0e20;

	std::vector< double > data;
	std::ifstream f( argv[1] );
	double in = 0.0;
	while( f >> in )	data.push_back( in );
	cout << data.size() << endl;

	while( dparams[0]*dparams[0] + dparams[1]*dparams[1]
		+ dparams[2]*dparams[2]  > 1.e-9 ) {

		for( size_t p = 0; p < 3; ++p ) {
			params[p] += dparams[p];
			HeatingRate rate( params[0], params[1] );
			rate.integrate();

			double sqerr = 0.0;
			for( size_t i = 0; i < 90; ++i ) {
				double err = rate.dndt_th( i*10 ) - params[2]*data[i+200];
				sqerr += err*err;
			}

			if( sqerr < cur_err ) {
				dparams[p] *= 1.1;
				cur_err = sqerr;
			} else {
				params[p] -= dparams[p];
				dparams[p] *= -0.9;
			}
		}

		//cout << params[0] << '\t' << params[1] << '\t' << params[2] << endl;
	}

	cout << "Parameters:" << endl;
	cout << "\tepsilon_bar: " << params[0] << endl;
	cout << "\tsigma: " << params[1] << endl;
	cout << "\tscale: " << params[2] << endl;

	ofstream out( argv[2] );

	HeatingRate rate( params[0], params[1] );
	rate.integrate();
	rate.output( out );
}

