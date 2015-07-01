
#include <iostream>
#include <algorithm>

#include "fem_data.hpp"

#include <fitsio.h>

#include <gsl/gsl_multimin.h>
#include <gsl/gsl_linalg.h>
#include <gsl/gsl_eigen.h>

// Helper class to convert C++ types to CFitsIO type constants
// Should be specialized as needed
template< typename T >
struct CFitsIOTypeMap {};
template<> struct CFitsIOTypeMap<float> { 
	const static int image_type = FLOAT_IMG;
	const static int type = TFLOAT; 
};
template<> struct CFitsIOTypeMap<short> { 
	const static int image_type = SHORT_IMG;
	const static int type = TSHORT; 
};

// Save a fits image of a 2D boost multi_array
template< typename T, size_t N >
void save_file( const std::string& filename, 
	const boost::multi_array< T, N >& img ) {

	fitsfile* f;
	int status = 0;

	// Initial exclamation point creates file if it doesn't exist
    std::string fname = "!" + filename;
	fits_create_file( &f, fname.c_str(), &status );
	
	long dims[N];
	for( size_t i = 0 ; i < N; ++i )
		dims[i] = img.shape()[i];

	typedef CFitsIOTypeMap< T > map;
	fits_create_img( f, map::image_type, N, dims, &status );
	fits_write_img( f, map::type, 1, img.num_elements(), 
		(void*)img.origin(), &status );
        
    fits_close_file( f, &status );

	if( status ) {
		fits_report_error( stderr, status );
	}
}

// Error function that will be used to fits the electric field to
// second order in each direction.
double fit_derivative_error( const gsl_vector *v, void* params ) {
	// v stores the field and its derivatives that we are fitting for

	float *p = (float*)params;
	// First parameter gives step size in each direction
	float d = *p++;

	// Second parameter tells whether fitting in two dimensions or three
	int is_3d = (int)(*p++);

	// Remaining parameters are either 9 (for 2D) or 27 (for 3D) 
	// electric field samples spaced at distance d
	float *samples = p;

	double error = 0.0f;
	for( int dx = -1; dx <=1; ++dx ) 
	for( int dy = -1; dy <= 1; ++dy )
	for( int dz = -is_3d; dz <= is_3d; ++dz ) {
		double Efx = gsl_vector_get( v, 0 )*dx*d + 
			gsl_vector_get( v, 1 )*dy*d +
			gsl_vector_get( v, 2 )*dz*d +
			gsl_vector_get( v, 6 ) + 
			gsl_vector_get( v, 9 )*dx*d*dx*d +
			gsl_vector_get( v, 10 )*dy*d*dy*d +
			gsl_vector_get( v, 11 )*dz*d*dz*d;
		double Efy = gsl_vector_get( v, 1 )*dx*d +
			gsl_vector_get( v, 3 )*dy*d +
			gsl_vector_get( v, 4 )*dz*d +
			gsl_vector_get( v, 7 ) +
			gsl_vector_get( v, 12 )*dx*d*dx*d +
			gsl_vector_get( v, 13 )*dy*d*dy*d +
			gsl_vector_get( v, 14 )*dz*d*dz*d;
		double Efz = gsl_vector_get( v, 2 )*dx*d +
			gsl_vector_get( v, 4 )*dy*d +
			gsl_vector_get( v, 5 )*dz*d +
			gsl_vector_get( v, 8 ) +
			gsl_vector_get( v, 15 )*dx*d*dx*d +
			gsl_vector_get( v, 16 )*dy*d*dy*d +
			gsl_vector_get( v, 17 )*dz*d*dz*d;
		float Efxsample = samples[ ((dz+is_3d)*9 + (dx+1)*3 + dy+1)*3 ];
		float Efysample = samples[ ((dz+is_3d)*9 + (dx+1)*3 + dy+1)*3 + 1 ];
		float Efzsample = samples[ ((dz+is_3d)*9 + (dx+1)*3 + dy+1)*3 + 2 ];

		error += sqrt( (Efx-Efxsample)*(Efx-Efxsample) + 
			(Efy-Efysample)*(Efy-Efysample) + 
			(Efz-Efzsample)*(Efz-Efzsample) );
	}

	return error;
}

// Fit electric field and derivatives in each direction
// Efield holds initial guesses for electric field and derivatives
// Esample holds the electric field sampled on a 3x3x3 grid at spacing h
void fit_field_derivatives( float Efield[18], float h, 
	float Esample[27][3], bool is_3d ) {

	const gsl_multimin_fminimizer_type *T =
		gsl_multimin_fminimizer_nmsimplex2;
	gsl_multimin_fminimizer *s = 0;
	gsl_multimin_function fn;

	gsl_vector *ss, *x;

	x = gsl_vector_alloc( 18 );
	for( size_t i = 0; i < 18; ++i )
		gsl_vector_set( x, i, Efield[i] );

	float params[83];
	params[0] = 1.0f;
	params[1] = (float)is_3d;
	for( size_t i = 0; i < 81; ++i )
		params[ 2+i ] = Esample[ i/3 ][i%3];

	ss = gsl_vector_alloc( 18 );
	gsl_vector_set_all( ss, 0.01 );

	fn.n = 18;
	fn.f = fit_derivative_error;
	fn.params = params;

	s = gsl_multimin_fminimizer_alloc( T, 18 );
	gsl_multimin_fminimizer_set( s, &fn, x, ss );

	int status = 0;
	size_t iter = 0;
	do {
		status = gsl_multimin_fminimizer_iterate( s );
		if( status )	break;

		double size = gsl_multimin_fminimizer_size( s );
		status = gsl_multimin_test_size( size, 1e-5 );
	} while( status == GSL_CONTINUE && ++iter < 1000 );

	for( size_t i = 0; i < 18; ++i )
		Efield[i] = gsl_vector_get( s->x, i );

	if( !is_3d ) {
		Efield[2] = Efield[4] = Efield[5] = Efield[8] = Efield[11] =
			Efield[14] = Efield[15] = Efield[16] = Efield[17] = 0.0f;
		Efield[5] = 1.0f;
	}

	gsl_vector_free( x );
	gsl_vector_free( ss );
	gsl_multimin_fminimizer_free( s );
	
}

// Error function for finding the field null based on electric field
// and its first and second derivative
double fit_null_error( const gsl_vector *pos, void* params ) {
	// params holds the field and its derivative
	float* Ef = (float*)params;

	// pos holds the current guess for the position of the field null
	double x = gsl_vector_get( pos, 0 ), 
		y = gsl_vector_get( pos, 1 ),
		z = gsl_vector_get( pos, 2 );

	// Calculate electric field at pos based on Ef
	double Ex = Ef[0]*x + Ef[1]*y + Ef[2]*z + Ef[6] + 
		Ef[9]*x*x + Ef[10]*y*y + Ef[11]*z*z;
	double Ey = Ef[1]*x + Ef[3]*y + Ef[4]*z + Ef[7] + 
		Ef[12]*x*x + Ef[13]*y*y + Ef[14]*z*z;
	double Ez = Ef[2]*x + Ef[4]*y + Ef[5]*z + Ef[8] + 
		Ef[15]*x*x + Ef[16]*y*y + Ef[17]*z*z;

	return sqrt( Ex*Ex + Ey*Ey + Ez*Ez );
}

void fit_field_null( float Efield[18], float v[3], 
	float a[3], float vec[3][3], bool is_3d ) {

	gsl_vector *b = gsl_vector_alloc( 3 ), *r = gsl_vector_alloc( 3 );
	for( size_t i = 0; i < 3; ++i ) {
		gsl_vector_set( b, i, -Efield[6+i] );
	}

	gsl_matrix* m = gsl_matrix_alloc( 3, 3 );
	gsl_matrix_set_zero( m );
	gsl_matrix_set( m, 0, 0, Efield[0] );
	gsl_matrix_set( m, 1, 0, Efield[1] );
	gsl_matrix_set( m, 2, 0, Efield[2] );
	gsl_matrix_set( m, 0, 1, Efield[1] );
	gsl_matrix_set( m, 1, 1, Efield[3] );
	gsl_matrix_set( m, 2, 1, Efield[4] );
	gsl_matrix_set( m, 0, 2, Efield[2] );
	gsl_matrix_set( m, 1, 2, Efield[4] );
	gsl_matrix_set( m, 2, 2, Efield[5] );

	int something;
	gsl_permutation *p = gsl_permutation_alloc( 3 );
	gsl_linalg_LU_decomp( m, p, &something );
	gsl_linalg_LU_solve( m, p, b, r );

	if( !is_3d )	
		gsl_vector_set( r, 2, 0.0 );

	gsl_vector_free( b );
	gsl_permutation_free( p );

	const gsl_multimin_fminimizer_type *T =
		gsl_multimin_fminimizer_nmsimplex2;
	gsl_multimin_fminimizer *s = 0;
	gsl_multimin_function fn;

	gsl_vector* ss = gsl_vector_alloc(3);
	gsl_vector_set_all( ss, 0.1 );

	fn.n = 3;
	fn.f = fit_null_error;
	fn.params = Efield;

	s = gsl_multimin_fminimizer_alloc( T, 3 );
	gsl_multimin_fminimizer_set( s, &fn, r, ss );

	int status = 0;
	size_t iter = 0;
	do {
		status = gsl_multimin_fminimizer_iterate( s );
		if( status )	break;

		double size = gsl_multimin_fminimizer_size( s );
		status = gsl_multimin_test_size( size, 1e-5 );
	} while( status == GSL_CONTINUE && ++iter < 1000 );

	for( size_t i = 0; i < 3; ++i )
		v[i] = gsl_vector_get( s->x, i );
	gsl_vector_free( r );

	gsl_matrix* vecs = gsl_matrix_alloc( 3, 3 );
	gsl_vector* as = gsl_vector_alloc( 3 );
	gsl_eigen_symmv_workspace* ws = gsl_eigen_symmv_alloc( 3 );

	// TODO: Maybe should be negative?
	gsl_matrix_set_zero( m );
	gsl_matrix_set( m, 0, 0, -Efield[0]/2.f );
	gsl_matrix_set( m, 1, 0, -Efield[1]/2.f );
	gsl_matrix_set( m, 2, 0, -Efield[2]/2.f );
	gsl_matrix_set( m, 0, 1, -Efield[1]/2.f );
	gsl_matrix_set( m, 1, 1, -Efield[3]/2.f );
	gsl_matrix_set( m, 2, 1, -Efield[4]/2.f );
	gsl_matrix_set( m, 0, 2, -Efield[2]/2.f );
	gsl_matrix_set( m, 1, 2, -Efield[4]/2.f );
	gsl_matrix_set( m, 2, 2, -Efield[5]/2.f );

	gsl_eigen_symmv( m, as, vecs, ws );
	for( size_t i = 0; i < 3; ++i ) {
		a[i] = gsl_vector_get( as, i );
		gsl_vector_view evec_i = gsl_matrix_column( vecs, i );
		vec[i][0] = gsl_vector_get( &evec_i.vector, 0 );
		vec[i][1] = gsl_vector_get( &evec_i.vector, 1 );
		vec[i][2] = gsl_vector_get( &evec_i.vector, 2 );
	}
	
	gsl_matrix_free( m );
	gsl_matrix_free( vecs );
	gsl_vector_free( as );
	gsl_eigen_symmv_free( ws );
}

const float FEMData::pi = 3.141592654;
const float FEMData::echarge = 1.60217657e-19;
const float FEMData::amu = 1.66053892e-27;

struct FitTrapParams {
	FEMData* fem;
	FEMData::vector_type goal_pos, goal_ws;

	std::vector<size_t> electrodes;
	std::vector<FEMData::voltage_type> rf;
	FEMData::RFData rf_data;
	double z_guess;
};

double fit_trap_error( const gsl_vector *pos, void* vparams ) {
	FitTrapParams* params = (FitTrapParams*)vparams;

	std::vector< FEMData::voltage_type > dc;
	double penalty = 0.0;
	for( size_t i = 0; i < pos->size; ++i ) {
		penalty += fabs( gsl_vector_get( pos, i ) ) * 1e9;
		dc.push_back( std::make_pair( params->electrodes[i*2],
			gsl_vector_get( pos, i ) ) );
		dc.push_back( std::make_pair( params->electrodes[i*2+1],
			gsl_vector_get( pos, i ) ) );
	}

	FEMData::TrapData trap = params->fem->rf_null( 
		params->rf, dc, params->rf_data, params->z_guess );

	if( isnan( trap.w[0] ) || isnan( trap.w[1] ) || isnan( trap.w[2] ) )
		return 1e100;


	return //penalty +
		1e11*(trap.x - params->goal_pos[0])*(trap.x - params->goal_pos[0]) +
		1e11*(trap.y - params->goal_pos[1])*(trap.y - params->goal_pos[1]) +
		1e11*(trap.z - params->goal_pos[2])*(trap.z - params->goal_pos[2]) +
		(trap.w[0] - params->goal_ws[0])*(trap.w[0] - params->goal_ws[0]) +
		(trap.w[1] - params->goal_ws[1])*(trap.w[1] - params->goal_ws[1]) +
		(trap.w[2] - params->goal_ws[2])*(trap.w[2] - params->goal_ws[2]);
}

void FEMData::find_trapping_potential( 
	vector_type position, vector_type strength,
	std::vector<voltage_type>& rf, std::vector<voltage_type>& dc_guess,
	RFData data, double z ) {

	size_t nvoltages = dc_guess.size();
	FitTrapParams params;
	params.fem = this;

	for( size_t i = 0; i < 3; ++i ) {
		params.goal_pos[i] = position[i];
		params.goal_ws[i] = strength[i];
	}

	for( size_t i = 0; i < nvoltages; ++i ) {
		params.electrodes.push_back( dc_guess[i].first );
	}

	params.rf = rf;
	params.rf_data = data;
	params.z_guess = z;

	const gsl_multimin_fminimizer_type *T =
		gsl_multimin_fminimizer_nmsimplex2;
	gsl_multimin_fminimizer *s = 0;
	gsl_multimin_function fn;

	nvoltages /= 2;
	gsl_vector* ss = gsl_vector_alloc( nvoltages );
	gsl_vector_set_all( ss, 1.5 );

	gsl_vector* x = gsl_vector_alloc( nvoltages );
	for( size_t i = 0; i < nvoltages; ++i )
		gsl_vector_set( x, i, dc_guess[i*2].second );

	fn.n = nvoltages;
	fn.f = fit_trap_error;
	fn.params = &params;

	s = gsl_multimin_fminimizer_alloc( T, nvoltages );
	gsl_multimin_fminimizer_set( s, &fn, x, ss );

	int status = 0;
	size_t iter = 0;
	do {
		status = gsl_multimin_fminimizer_iterate( s );
		if( status )	break;

		double size = gsl_multimin_fminimizer_size( s );
		status = gsl_multimin_test_size( size, 1e-6 );
	} while( status == GSL_CONTINUE && ++iter < 1000 );

	for( size_t i = 0; i < nvoltages; ++i ) {
		dc_guess[i*2].second = gsl_vector_get( s->x, i );
		dc_guess[i*2+1].second = gsl_vector_get( s->x, i );
	}

	gsl_vector_free( x );
	gsl_vector_free( ss );
	gsl_multimin_fminimizer_free( s );
}

FEMData::TrapData FEMData::rf_null( std::vector<voltage_type>& rf,
	std::vector<voltage_type>& dc,
	RFData data, float z ) {

	size_t* sdims = get_dimensions();
	boost::array< index_type, 4 > field_size = 
		{{3, sdims[0], sdims[1], sdims[2]}};
	field_type rf_field( field_size );

	boost::array< index_type, 3 > pot_size = {{sdims[0], sdims[1], sdims[2]}};
	potential_type dc_pot( pot_size );

	rf_field = get_field( rf );
	dc_pot = get_potential( dc );

	typedef potential_slice_type::index_range range;
	potential_slice_type::index_gen indices;
	potential_slice_type::size_type s0 = dc_pot.shape()[0];
	potential_slice_type::size_type s1 = dc_pot.shape()[1];
	potential_slice_type::size_type s2 = dc_pot.shape()[2];

	// rf pseudopotential in V
	potential_type pseudo_pot( 
		boost::extents[rf_field.shape()[1]]
			[rf_field.shape()[2]][rf_field.shape()[3]], 
		boost::fortran_storage_order() ); 

	potential_type full_pot(
		boost::extents[rf_field.shape()[1]]
			[rf_field.shape()[2]][rf_field.shape()[3]], 
		boost::fortran_storage_order() ); 
		
	for( field_type::index x = 0; x < rf_field.shape()[1]; ++x )
	for( field_type::index y = 0; y < rf_field.shape()[2]; ++y )
	for( field_type::index z = 0; z < rf_field.shape()[3]; ++z ) {
		pseudo_pot[x][y][z] = data.Z*data.Z * echarge*echarge /
			(4 * data.m * amu * data.w*data.w) * (
			rf_field[0][x][y][z]*rf_field[0][x][y][z] +
			rf_field[1][x][y][z]*rf_field[1][x][y][z] +
			rf_field[2][x][y][z]*rf_field[2][x][y][z] ) / echarge;
		full_pot[x][y][z] = pseudo_pot[x][y][z] + dc_pot[x][y][z];
	}

	potential_slice_type yz_dc =
		full_pot[ indices[ 15 ][ range( 0, s1 ) ][ range( 0, s2 ) ] ];
	boost::array< potential_type::index, 2 > dims = {{s2, s1}};
	yz_dc.reshape( dims );
	save_file( "yz_dc.fits", yz_dc );

	potential_slice_type xz_dc =
		full_pot[ indices[ range(0, s0) ][ 26 ][ range(0, s2) ] ];
	boost::array< potential_type::index, 2 > dims2 = {{s2, s0}};
	xz_dc.reshape( dims2 );

	save_file( "xz_dc.fits", xz_dc );

	for( size_t i = 1; i <= 16; ++i ) {
		std::vector< voltage_type > test_voltages;
		test_voltages.push_back( std::make_pair( i, 1.0 ) );
		dc_pot = get_potential( test_voltages );

		std::stringstream ss;
		ss << i;
		std::string name = "yz_dc" + ss.str() + ".fits";
		potential_slice_type yz_dc =
			dc_pot[ indices[ 15 ][ range( 0, s1 ) ][ range( 0, s2 ) ] ];
		boost::array< potential_type::index, 2 > dims = {{s2, s1}};
		yz_dc.reshape( dims );
		save_file( name, yz_dc );

		name = "xz_dc" + ss.str() + ".fits";
		potential_slice_type xz_dc =
			dc_pot[ indices[ range(0, s0) ][ 26 ][ range(0, s2) ] ];
		boost::array< potential_type::index, 2 > dims2 = {{s2, s0}};
		xz_dc.reshape( dims2 );

		save_file( name, xz_dc );
	}

	potential_slice_type pot = slice_z( full_pot, z );
	potential_slice_type pseudo_z = slice_z( pseudo_pot, z );
	save_file( "pseudo.fits", pseudo_z );
	save_file( "dc.fits", slice_z( dc_pot, z ) );
	save_file( "pot.fits", pot );

	// Make initial guess for null as minimum of pseudopotential
	float* elem = std::min_element( pseudo_z.origin(), 
		pseudo_z.origin() + pseudo_z.num_elements() );
	size_t off = elem - pseudo_z.origin();

	vector_type null = { off % pot.shape()[0], off / pot.shape()[0], z };
	//std::cout << "Initial trap null estimate: " << null[0] << ", " << 
		//null[1] << ", " << null[2] << std::endl;

	TrapData trap_2d = find_null_2d( pot, data, null );
	TrapData trap_3d = find_null_3d( full_pot, data, null );

	//pot = slice_z( full_pot, null[2] );
	//save_file( "final_pot.fits", pot );

	return trap_3d;
}

FEMData::TrapData FEMData::find_null_2d( const potential_slice_type& pot, 
	RFData& data, vector_type null ) {

	float Efit[18];
	vector_type Esample[27];

	float dnull = 1.0;
	vector_type evals, evecs[3];

	potential_slice_type::size_type s0 = pot.shape()[0];
	potential_slice_type::size_type s1 = pot.shape()[1];

	while( dnull > 0.02 ) {
		// TODO: hard coded factor of 2 from GTRI
		for( int dx = -1; dx <= 1; ++dx ) for( int dy = -1; dy <= 1; ++dy ) {
			vector_type pt = { null[0] + dx, null[1] + 2.f*dy, 0 };
			sample_derivatives( pot, pt, 0.01, Esample[ (dx+1)*3 + dy+1 ] );
		}

		// Fit electric field at 9 points to basis functions
		// 1., x, y, z, x^2, y^2, z^2
		
		// Initial guesses for first derivatives
		Efit[0] = ( Esample[7][0] - Esample[1][0] ) / 2.f;		// Ex/dx
		Efit[1] = ( Esample[7][1] - Esample[1][1] + 
			Esample[5][0] - Esample[3][0] ) / 4.f;				// Ex/dy
		Efit[2] = 0.0f;											// Ex/dz
		Efit[3] = ( Esample[5][1] - Esample[3][1] ) / 2.f;		// Ey/dy
		Efit[4] = 0.0f;											// Ey/dz
		Efit[5] = 0.0f;											// Ez/dz

		// Initial guesses for constant offsets
		Efit[6] = Esample[4][0];
		Efit[7] = Esample[4][1];
		Efit[8] = Esample[4][2];

		for( size_t i = 0; i < 3; ++i ) {
			// Guess for Ex^2/di^2, Ey^2/di^2, Ez^2/di^2
			Efit[ 9 + i ] = ( Esample[7][i] + Esample[1][i] ) / 2.f;
			Efit[ 12 + i ] = ( Esample[5][i] + Esample[3][i] ) / 2.f;
			Efit[ 15 + i ] = 0.f;
		}

		vector_type offset;
		fit_field_derivatives( Efit, 1.0, Esample, false );
		fit_field_null( Efit, offset, evals, evecs, false );

		if( null[0] + offset[0] < 4 || null[0] + offset[0] > s0 - 4 || 
			null[1] + offset[1] < 4 || null[1] + offset[1] > s1 - 4 ) {
			evals[0] = evals[1] = evals[2] = -1.0;
			break;
		}

		null[0] += offset[0];
		null[1] += offset[1];
		dnull = fabsf( offset[0] ) + fabsf( offset[1] );
	}

	TrapData result;
	result.x = null[0];		result.y = null[1];		result.z = null[2];
	
	for( size_t i = 0; i < 3; ++i ) {
		result.w[i] = sqrt(2*0.5e12 * evals[i] * data.Z*echarge / 
			data.m / amu) / 2 / pi;
		std::copy( evecs[i], evecs[i]+3, result.axes[i] );
	}

	return result;
}

FEMData::TrapData FEMData::find_null_3d( const potential_type& pot,
	RFData& data, vector_type null ) {

	float Efit[18];
	vector_type Esample[27];

	float dnull = 1.0;
	vector_type evals, evecs[3];

	potential_type::size_type s0 = pot.shape()[0];
	potential_type::size_type s1 = pot.shape()[1];
	potential_type::size_type s2 = pot.shape()[2];

	while( dnull > 0.02 ) {
		// TODO: hard coded factor of 2 from GTRI
		for( int dx = -1; dx <= 1; ++dx ) 
		for( int dy = -1; dy <= 1; ++dy )  
		for( int dz = -1; dz <= 1; ++dz ) {
			vector_type pt = { null[0] + dx, null[1] + 2.f*dy, 
				null[2] + 2.f*dz };
			sample_derivatives( pot, pt, 0.01, 
				Esample[ (dz+1)*9 + (dx+1)*3 + dy+1 ] );
		}

		// Fit electric field at 9 points to basis functions
		// 1., x, y, z, x^2, y^2, z^2
		
		// Initial guesses for first derivatives
		Efit[0] = ( Esample[9+7][0] - Esample[9+1][0] ) / 2.f;		// Ex/dx
		Efit[1] = ( Esample[9+7][1] - Esample[9+1][1] + 
			Esample[9+5][0] - Esample[9+3][0] ) / 4.f;				// Ex/dy
		Efit[2] = ( Esample[9+7][2] - Esample[9+1][2] +
			Esample[18+4][0] - Esample[0+4][0] ) / 4.f;				// Ex/dz
		Efit[3] = ( Esample[9+5][1] - Esample[9+3][1] ) / 2.f;		// Ey/dy
		Efit[4] = ( Esample[9+5][2] - Esample[9+3][2] +
			Esample[18+4][1] - Esample[0+4][1] ) / 4.f;				// Ey/dz
		Efit[5] = ( Esample[18+4][2] - Esample[0+4][2] )/ 2.f;		// Ez/dz

		// Initial guesses for constant offsets
		Efit[6] = Esample[4][0];
		Efit[7] = Esample[4][1];
		Efit[8] = Esample[4][2];

		for( size_t i = 0; i < 3; ++i ) {
			// Guess for Ex^2/di^2, Ey^2/di^2, Ez^2/di^2
			Efit[ 9 + i ] = ( Esample[9+7][i] + Esample[9+1][i] ) / 2.f;
			Efit[ 12 + i ] = ( Esample[9+5][i] + Esample[9+3][i] ) / 2.f;
			Efit[ 15 + i ] = ( Esample[18+4][i] + Esample[0+4][i] ) / 2.f;
		}

		vector_type offset;
		fit_field_derivatives( Efit, 1.0, Esample, true );
		fit_field_null( Efit, offset, evals, evecs, true );

		if( null[0] + offset[0] < 4 || null[0] + offset[0] > s0 - 4 || 
			null[1] + offset[1] < 4 || null[1] + offset[1] > s1 - 4 ||
			null[2] + offset[2] < 4 || null[2] + offset[2] > s2 - 4 ) {
			evals[0] = evals[1] = evals[2] = -1.0;
			break;
		}

		null[0] += offset[0];
		null[1] += offset[1];
		null[2] += offset[2];
		dnull = fabsf( offset[0] ) + fabsf( offset[1] ) + fabsf( offset[2] );
	}

	TrapData result;
	result.x = null[0];		result.y = null[1];		result.z = null[2];
	
	for( size_t j = 0; j < 3; ++j ) 
	for( size_t i = 0; i < 3; ++i ) {
		if( fabs( evecs[i][j] ) > 0.707 ) {
			result.w[j] = sqrt(2*0.5e12 * evals[i] * data.Z*echarge / 
				data.m / amu) / 2 / pi;
			std::copy( evecs[i], evecs[i]+3, result.axes[j] );
		}
	}

	return result;
}

FEMData::slice_type FEMData::potential( field_type E ) {
	slice_type potential( boost::extents
		[E.shape()[1]][E.shape()[2]][E.shape()[3]] );

	// TODO Hard coded factor of 2 from GTRI
	potential[0][0][0] = 0.;
	for( field_type::index x = 1; x < E.shape()[1]; ++x )
		potential[x][0][0] = potential[x-1][0][0] - E[0][x-1][0][0] * 2e-6;

	for( field_type::index y = 1; y < E.shape()[2]; ++y )
	for( field_type::index x = 0; x < E.shape()[1]; ++x )
		potential[x][y][0] = potential[x][y-1][0] - E[1][x][y-1][0] * 1e-6;

	for( field_type::index z = 1; z < E.shape()[3]; ++z )
	for( field_type::index y = 0; y < E.shape()[2]; ++y )
	for( field_type::index x = 0; x < E.shape()[1]; ++x )
		potential[x][y][z] = potential[x][y][z-1] - E[2][x][y][z-1] * 1e-6;

	return potential;
}

FEMData::field_type FEMData::field( potential_type potential, bool microns ) {
	// TODO: implement correct offset to find actual trap position
	field_type field( boost::extents[3]
		[potential.shape()[0]][potential.shape()[1]][potential.shape()[2]] );

	float E[3];
	float* data = field.origin();
	for( field_type::index x = 2; x < potential.shape()[0]-2; ++x )
	for( field_type::index y = 2; y < potential.shape()[1]-2; ++y )
	for( field_type::index z = 2; z < potential.shape()[2]-2; ++z ) {
		vector_type pt = {x, y, z};
		sample_derivatives( potential, pt, 0.1, E );
		for( size_t i = 0; i < 3; ++i )
			field[i][x][y][z] = microns? E[i] / 1e-6: E[i];
	}

	for( field_type::index y = 2; y < potential.shape()[1]-2; ++y )
	for( field_type::index z = 2; z < potential.shape()[2]-2; ++z ) {
		for( size_t i = 0; i < 3; ++i ) {
			size_t m = potential.shape()[0];
			field[i][0][y][z] = field[i][1][y][z] = field[i][2][y][z];
			field[i][m-1][y][z] = field[i][m-2][y][z] = field[i][m-3][y][z];
		}
	}

	for( field_type::index x = 0; x < potential.shape()[0]; ++x )
	for( field_type::index z = 2; z < potential.shape()[2]-2; ++z ) {
		for( size_t i = 0; i < 3; ++i ) {
			size_t m = potential.shape()[1];
			field[i][x][0][z] = field[i][x][1][z] = field[i][x][2][z];
			field[i][x][m-1][z] = field[i][x][m-2][z] = field[i][x][m-3][z];
		}
	}

	for( field_type::index x = 0; x < potential.shape()[0]; ++x )
	for( field_type::index y = 0; y < potential.shape()[1]; ++y ) {
		for( size_t i = 0; i < 3; ++i ) {
			size_t m = potential.shape()[2];
			field[i][x][y][0] = field[i][x][y][1] = field[i][x][y][2];
			field[i][x][y][m-1] = field[i][x][y][m-2] = field[i][x][y][m-3];
		}
	}

	return field;
}

FEMData::slice_type FEMData::slice_z( field_type E, float zf ) {
	index_type z(zf);
	float t = z - zf;
	slice_type result( boost::extents[3][E.shape()[1]][E.shape()[2]] );

	for( field_type::index x = 0; x < E.shape()[1]; ++x )
	for( field_type::index y = 0; y < E.shape()[2]; ++y )
	for( field_type::index t = 0; t < 3; ++t ) {
		result[t][x][y] =  (1-t)*E[t][x][y][z] + t*E[t][x][y][z+1];
	}

	return result;
}

FEMData::potential_slice_type FEMData::slice_z( potential_type pot, float zf ) {
	index_type z(zf);
	float t = z - zf;
	potential_slice_type result( 
		boost::extents[pot.shape()[0]][pot.shape()[1]],
		boost::fortran_storage_order() ); 

	for( potential_type::index x = 0; x < pot.shape()[0]; ++x )
	for( potential_type::index y = 0; y < pot.shape()[1]; ++y ) {
		result[x][y] = (1-t)*pot[x][y][z] + t*pot[x][y][z+1];
	}

	return result;
}

float p( float t, float a0, float a1, float a2, float a3 ) {
	float temp[4];
	temp[0] = 2 * a1;
	temp[1] = -a0 + a2;
	temp[2] = 2*a0 - 5*a1 + 4*a2 -a3;
	temp[3] = -a0 + 3*a1 - 3*a2 + a3;

	return 0.5f * (temp[0] + t*temp[1] + t*t*temp[2] + t*t*t*temp[3]);
}

float FEMData::sample( const potential_line_type& pot, vector_type pt ) {
	potential_type::index idx = pt[0];
	return p( pt[0] - idx,
		pot[ idx-1 ], pot[ idx-0 ], pot[ idx+1 ], pot[ idx+2 ] );
	
}

float FEMData::sample( const potential_slice_type& pot, vector_type pt ) {
	potential_type::index idx = pt[1];
	typedef potential_slice_type::index_range range;
	potential_slice_type::index_gen indices;
	potential_slice_type::size_type s = pot.shape()[0];

	return p( pt[1] - idx,
		sample( pot[ indices[ range(0, s) ][ idx-1 ] ], pt ),
		sample( pot[ indices[ range(0, s) ][ idx-0 ] ], pt ),
		sample( pot[ indices[ range(0, s) ][ idx+1 ] ], pt ),
		sample( pot[ indices[ range(0, s) ][ idx+2 ] ], pt ) );
}

float FEMData::sample( const potential_type& pot, vector_type pt ) {
	potential_type::index idx = pt[2];
	typedef potential_slice_type::index_range range;
	potential_slice_type::index_gen indices;
	potential_slice_type::size_type s0 = pot.shape()[0];
	potential_slice_type::size_type s1 = pot.shape()[1];

	return p( pt[2] - idx,
		sample( pot[ indices[ range(0, s0) ][ range(0, s1) ][ idx-1 ] ], pt ),
		sample( pot[ indices[ range(0, s0) ][ range(0, s1) ][ idx-0 ] ], pt ),
		sample( pot[ indices[ range(0, s0) ][ range(0, s1) ][ idx+1 ] ], pt ),
		sample( pot[ indices[ range(0, s0) ][ range(0, s1) ][ idx+2 ] ], pt ) );
}

float FEMData::sample_derivatives( const potential_slice_type& pot, 
	vector_type pt, float h, float* E ) {

	// TODO: Hard coded factor of 2 from GTRI
	vector_type ptx1 = {pt[0]-h, pt[1], pt[2]}, ptx2 = {pt[0]+h, pt[1], pt[2]};
	E[0] = -( sample( pot, ptx2 ) - sample( pot, ptx1 ) ) / 2.f / 2.f / h;

	vector_type pty1 = {pt[0], pt[1]-h, pt[2]}, pty2 = {pt[0], pt[1]+h, pt[2]};
	E[1] = -( sample( pot, pty2 ) - sample( pot, pty1 ) ) / 2.f / h;

	E[2] = 0.0f;
}

float FEMData::sample_derivatives( const potential_type& pot, 
	vector_type pt, float h, float* E ) {

	// TODO: Hard coded factor of 2 from GTRI
	vector_type ptx1 = {pt[0]-h, pt[1], pt[2]}, ptx2 = {pt[0]+h, pt[1], pt[2]};
	E[0] = -( sample( pot, ptx2 ) - sample( pot, ptx1 ) ) / 2.f / 2.f / h;

	vector_type pty1 = {pt[0], pt[1]-h, pt[2]}, pty2 = {pt[0], pt[1]+h, pt[2]};
	E[1] = -( sample( pot, pty2 ) - sample( pot, pty1 ) ) / 2.f / h;

	vector_type ptz1 = {pt[0], pt[1], pt[2]-h}, ptz2 = {pt[0], pt[1], pt[2]+h};
	E[2] = -( sample( pot, ptz2 ) - sample( pot, ptz1 ) ) / 2.f / h;
}
