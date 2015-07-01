
#include <iostream>
#include <sstream>
#include "hdf5.h"

#include "load_gtri.hpp"

GTRIData::GTRIData( const std::string& filex_, const std::string& filey_,
	const std::string& filez_, const std::string& attr ):
	filex( filex_ ), filey( filey_ ), filez( filez_ ), attrname( attr ) {

	load_dimensions( filex );
	std::cout << "Loading GTRI FEM file..." << std::endl;
	std::cout << "Dimensions: " << 
		dims[0] << ", " << dims[1] << ", " << dims[2] << std::endl;
	std::cout << "Resolution (microns): " << 
		deltas[0] << ", " << deltas[1] << ", " << deltas[2] << std::endl;
	
	load_file( filex, 0, false );
	load_file( filey, 1, false );
	load_file( filez, 2, false );
	std::cout << "Finished loading files." << std::endl;
}

GTRIData::GTRIData( const std::string& pot_, const std::string& attr ):
	filepot( pot_ ), attrname( attr ) {

	// TODO: Don't allocate space for 3 component field here
	std::cout << "Loading GTRI FEM file..." << std::endl;
	load_dimensions( filepot );
	std::cout << "Dimensions: " << 
		dims[0] << ", " << dims[1] << ", " << dims[2] << std::endl;
	std::cout << "Resolution (microns): " << 
		deltas[0] << ", " << deltas[1] << ", " << deltas[2] << std::endl;
	
	load_file( filepot, 0, true );
}

void GTRIData::load_dimensions( const std::string& filename ) {
	hid_t file, group, data;
	herr_t status;

	file = H5Fopen( filename.c_str(), H5F_ACC_RDONLY, H5P_DEFAULT );
	group = H5Gopen1( file, "Attributes" );
	data = H5Dopen1( group, "Extents" );
		
	hid_t space, type;
	hsize_t ds[3], ndims;

	space = H5Dget_space( data );
	ndims = H5Sget_simple_extent_dims( space, ds, NULL );
	if( (ndims != 1 && (ndims != 2 || ds[1] != 1)) || ds[0] != 3 ) {
		std::cerr << "Could not read dimensions" << std::endl;
		return;
	}

	H5Dread( data, H5T_NATIVE_HSIZE, H5S_ALL, H5S_ALL, H5P_DEFAULT, dims );
		
	nelements = dims[0]*dims[1]*dims[2];
	for( size_t i = 0; i <= 63; ++i )
		electrodes.push_back( GTRIElectrodeData( i, dims ) );
		
	status = H5Dclose( data );
	data = H5Dopen1( group, "Deltas" );

	space = H5Dget_space( data );
	ndims = H5Sget_simple_extent_dims( space, ds, NULL );
	if( (ndims != 1 && (ndims != 2 || ds[1] != 1)) || ds[0] != 3 ) {
		std::cerr << "Could not read deltas" << std::endl;
		return;
	}

	H5Dread(data, H5T_NATIVE_FLOAT, H5S_ALL, H5S_ALL, H5P_DEFAULT, deltas);

	status = H5Dclose( data );
	status = H5Fclose( file );
}


void GTRIData::load_file( const std::string& filename, index_type offset,
	bool potential ) {
	hid_t file, group, data;
	herr_t status;

	file = H5Fopen( filename.c_str(), H5F_ACC_RDONLY, H5P_DEFAULT );
	group = H5Gopen1( file, attrname.c_str() );

	// Suppress default error messages when testing for electrodes
	H5Eset_auto2( H5E_DEFAULT, 0, 0 );
	
	for( size_t i = 0; i <= 100; ++i ) {
		std::stringstream ss;
		ss << i;

		data = H5Dopen1( group, ss.str().c_str() );
		if( data < 0 ) {
			//std::cout << "Could not load electrode: " << i << std::endl;
			continue;
		}
		
		hid_t space, type;
		space = H5Dget_space( data );
		type = H5Dget_type( data );

		hsize_t ds[3] = {1,1,1}, ndims;
		ndims = H5Sget_simple_extent_dims( space, ds, NULL );
		
		H5T_class_t t_class;
		t_class = H5Tget_class( type );

		if( t_class != H5T_FLOAT || 
			//ndims != 3 || ds[0] != dims[0] ||
		 	//ds[1] != dims[1] || ds[2] != dims[2]
			ds[0]*ds[1]*ds[2] != dims[0]*dims[1]*dims[2] ) {
			std::cout << "Bad data for electrode: " << i << std::endl;
			continue;
		}

		boost::multi_array<float, 3> array( 
			boost::extents[dims[0]][dims[1]][dims[2]], 
			boost::fortran_storage_order() );

		float* fdata = electrodes[i].field.origin();
		fdata += offset;

		status = H5Dread( data, H5T_NATIVE_FLOAT, H5S_ALL, H5S_ALL,
			H5P_DEFAULT, array.origin() );
		status = H5Dclose( data );

		if( potential ) {
			electrodes[i].potential = array;
			electrodes[i].has_potential = true;
		} else {
			electrodes[i].field[offset] = array;
			electrodes[i].has_field = true;
		}
	}

	status = H5Fclose( file );
}

GTRIData::field_type GTRIData::get_field( std::vector<voltage_type>& voltages,
	range_type* dimensions ) {

	boost::array< index_type, 4 > arr = {{3, dims[0], dims[1], dims[2]}};
	field_type field( arr );

	float* out = field.origin();
	for( size_t i = 0; i < voltages.size(); ++i ) {
		if( !electrodes[ voltages[i].first ].has_field ) {
			electrodes[ voltages[i].first ].field = FEMData::field(
				electrodes[ voltages[i].first ].potential, true );
			electrodes[ voltages[i].first ].has_field = true;
		}

		float* data = electrodes[ voltages[i].first ].field.origin();
		for( size_t j = 0; j < nelements*3; ++j )
			out[j] += data[j] * voltages[i].second;
	}

	return field;
}

GTRIData::potential_type GTRIData::get_potential( 
	std::vector<voltage_type>& voltages, range_type* dimensions ) {

	boost::array< index_type, 3 > arr = {{dims[0], dims[1], dims[2]}};
	potential_type pot( arr );

	float* out = pot.origin();
	for( size_t i = 0; i < voltages.size(); ++i ) {
		if( !electrodes[ voltages[i].first ].has_potential ) {
			electrodes[ voltages[i].first ].potential = potential(
				electrodes[ voltages[i].first ].field );
			electrodes[ voltages[i].first ].has_potential = true;
		}

		float* data = electrodes[ voltages[i].first ].potential.origin();
		for( size_t j = 0; j < nelements; ++j )
			out[j] += data[j] * voltages[i].second;
	}

	return pot;
}


