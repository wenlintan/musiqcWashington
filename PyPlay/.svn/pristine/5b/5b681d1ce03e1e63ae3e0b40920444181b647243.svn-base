
#include <string>
#include <vector>
#include "fem_data.hpp"

struct GTRIElectrodeData {
	typedef FEMData::field_type field_type;
	typedef FEMData::potential_type potential_type;
	typedef field_type::size_type size_type;

	GTRIElectrodeData( size_t electrode, size_type* dim ):
		electrode_number( electrode ),
		has_field( false ), has_potential( false ) {

		boost::array< size_type, 4 > field_extents = 
		    {{3, dim[0], dim[1], dim[2]}};
		field.resize( field_extents );

		boost::array< size_type, 3 > pot_extents =
		    {{dim[0], dim[1], dim[2]}};
		potential.resize( pot_extents );
	}

	size_t electrode_number;
	bool has_field, has_potential;
	field_type field;
	potential_type potential;
};

class GTRIData: public FEMData {
	std::vector< GTRIElectrodeData > electrodes;
	std::string	filepot, filex, filey, filez, attrname;

	size_type nelements;
	size_type dims[3];
	float deltas[3];

public:
	typedef size_t electrode_type;	
	GTRIData( const std::string& xfile,
		const std::string& yfile, const std::string& zfile, 
		const std::string& attr );

	GTRIData( const std::string& pot, const std::string& attr );

private:
	void load_dimensions( const std::string& filename );
	void load_file( const std::string& filename, index_type offset,
	    bool potential );

	size_type* get_dimensions() { return dims; }
	float* get_deltas() { return deltas; }

	field_type get_field( std::vector<voltage_type>& voltages,
	    range_type* dimensions = 0 );

	potential_type get_potential( std::vector<voltage_type>& voltages,
	    range_type* dimensions = 0 );
};

	
