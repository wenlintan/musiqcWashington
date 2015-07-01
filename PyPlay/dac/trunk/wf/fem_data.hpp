
#include <vector>
#include <boost/multi_array.hpp>

class FEMData {
public:

	typedef boost::multi_array<float, 3> potential_type;
	typedef boost::multi_array<float, 4> field_type;

	typedef field_type::index index_type;
	typedef field_type::size_type size_type;

	typedef std::pair< index_type, index_type > range_type;
	typedef std::pair<index_type, float> voltage_type;

	typedef float vector_type[3];

	struct RFData {
		float Z, m, w;
	};

	struct PseudoData {
		float x, y, z;
		vector_type axes[2];
		float w[2];
	};

	struct TrapData {
		float x, y, z;
		vector_type axes[3];
		float w[3];
	};

	struct AxialPolynomialData {
		TrapData trap;
		float axial_c[4];
	};
		
	TrapData rf_null( std::vector<voltage_type>& rf_electrodes, 
		std::vector<voltage_type>& dc,
		RFData data, float z  );

	void find_trapping_potential( vector_type position, vector_type strength,
		std::vector<voltage_type>& rf, std::vector<voltage_type>& dc_guess,
		RFData data, double z );

	TrapData trap_axes( PseudoData rf, 
		std::vector<voltage_type> voltages );

	AxialPolynomialData axial_polynomial( PseudoData rf,
		std::vector<voltage_type> voltages );

protected:
	const static float echarge;
	const static float amu;
	const static float pi;

	typedef boost::multi_array<float, 3> slice_type;
	typedef boost::multi_array<float, 2> potential_slice_type;
	typedef boost::multi_array<float, 1> potential_line_type;

	TrapData find_null_2d( const potential_slice_type& p, RFData& data, 
		vector_type guess );
	TrapData find_null_3d( const potential_type& p, RFData& data,
		vector_type guess );

	potential_type potential( field_type field );
	field_type field( potential_type potential, bool microns = false );

	slice_type slice_z( field_type field, float z );
	potential_slice_type slice_z( potential_type pot, float z );

	float sample( const potential_line_type& pot, vector_type pt );
	float sample( const potential_slice_type& pot, vector_type pt );
	float sample( const potential_type& pot, vector_type pt );

	float sample_derivatives( const potential_slice_type& pot, vector_type pt,
		float h, float* E );
	float sample_derivatives( const potential_type& pot, vector_type pt,
		float h, float* E );

	virtual size_type* get_dimensions() = 0;
	virtual float* get_deltas() = 0;

	virtual field_type get_field( std::vector<voltage_type>& voltages,
		range_type* dimensions = 0 ) = 0;

	virtual potential_type get_potential( std::vector<voltage_type>& voltages,
		range_type* dimensions = 0 ) = 0;
};

