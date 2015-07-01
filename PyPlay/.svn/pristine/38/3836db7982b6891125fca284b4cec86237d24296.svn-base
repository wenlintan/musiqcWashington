
#include <fstream>

#include <boost/assign/list_of.hpp>
#include "load_gtri.hpp"

int main( int argc, char** argv ) {
	//GTRIData data( "postEx.h5", "postEy.h5", "postEz.h5",
		 //"Attributes/potentialDueToSurface" );
	GTRIData data( "output.h5", "Attributes/potentialDueToSurface" );

	GTRIData::RFData ytterbiumdata = { 1, 171, 2*3.141592654*35e6 };
	GTRIData::RFData bariumdata = { 1, 138, 2*3.141592654*24e6 };
	GTRIData::RFData calciumdata = { 1, 40, 2*3.141592654*44.7e6 };

	std::vector<GTRIData::voltage_type> rf = 
		boost::assign::list_of( std::make_pair(61, 93.) );
	std::vector<GTRIData::voltage_type> harmonic_rot =
		boost::assign::list_of
			( std::make_pair(21, 1.8*-0.364988) )
			( std::make_pair(22, 1.8*-0.5638) )
			( std::make_pair(23, 1.8*-0.166484) )
			( std::make_pair(24, 1.8*-0.787350) )
			( std::make_pair(25, 1.8*-0.724012) )

			( std::make_pair(31, 1.8*1.703309) )
			( std::make_pair(32, 1.8*-4.422963) )
			( std::make_pair(33, 1.8*1.533470) )
			( std::make_pair(34, 1.8*2.173730) )
			( std::make_pair(35, 1.8*1.122751) )
			;

	std::vector<GTRIData::voltage_type> harmonic =
		boost::assign::list_of
			( std::make_pair(21, 0.651478) )
			( std::make_pair(22, -2.502890) )
			( std::make_pair(23, 0.691130) )
			( std::make_pair(24, 0.677477) )
			( std::make_pair(25, 0.192933) )

			( std::make_pair(31, 0.661701) )
			( std::make_pair(32, -2.497315) )
			( std::make_pair(33, 0.688821) )
			( std::make_pair(34, 0.681343) )
			( std::make_pair(35, 0.194750) )
			;

	std::vector<GTRIData::voltage_type> to36 =
		boost::assign::list_of
			( std::make_pair(21, 1.85*-0.6194) )
			( std::make_pair(22, 1.85*-1.2962) )
			( std::make_pair(23, 1.85*-0.8154) )
			( std::make_pair(24, 1.85*-0.8271) )
			( std::make_pair(25, 1.85*-0.0) )

			( std::make_pair(31, 1.85*1.6454) )
			( std::make_pair(32, 1.85*-5.4703) )
			( std::make_pair(33, 1.85*1.2584) )
			( std::make_pair(34, 1.85*2.5367) )
			( std::make_pair(35, 1.85*0.0) )

			( std::make_pair(62, 1.85*-0.24) )
			;

	std::vector<GTRIData::voltage_type> hoa_rf =
		boost::assign::list_of( std::make_pair(0, 250.) );
	std::vector<GTRIData::voltage_type> hoa_dc_1MHz =
		boost::assign::list_of
			( std::make_pair(1, 1*0.2663) )
			( std::make_pair(2, 1*0.2669) )
			( std::make_pair(3, 1*0.9281) )
			( std::make_pair(4, 1*0.9335) )
			( std::make_pair(5, 1*1.5874) )
			( std::make_pair(6, 1*1.5977) )
			( std::make_pair(7, 1*-2.1085) )
			( std::make_pair(8, 1*-2.1226) )
			( std::make_pair(9, 1*1.5881) )
			( std::make_pair(10, 1*1.5971) )
			( std::make_pair(11, 1*0.9296) )
			( std::make_pair(12, 1*0.9326) )
			( std::make_pair(13, 1*0.2663) )
			( std::make_pair(14, 1*0.2669) )
			( std::make_pair(15, 1*0.0000) )
			( std::make_pair(16, 1*0.0000) )
			;
	std::vector<GTRIData::voltage_type> hoa_dc_1MHz_9 =
		boost::assign::list_of
			( std::make_pair(1, 1*0.0000) )
			( std::make_pair(2, 1*0.0000) )
			( std::make_pair(3, 1*0.2663) )
			( std::make_pair(4, 1*0.2669) )
			( std::make_pair(5, 1*0.9281) )
			( std::make_pair(6, 1*0.9335) )
			( std::make_pair(7, 1*1.5874) )
			( std::make_pair(8, 1*1.5977) )
			( std::make_pair(9, 1*-2.1085) )
			( std::make_pair(10, 1*-2.1226) )
			( std::make_pair(11, 1*1.5881) )
			( std::make_pair(12, 1*1.5971) )
			( std::make_pair(13, 1*0.9296) )
			( std::make_pair(14, 1*0.9326) )
			( std::make_pair(15, 1*0.2663) )
			( std::make_pair(16, 1*0.2669) )
			;
	std::vector<GTRIData::voltage_type> hoa_dc_250kHz =
		boost::assign::list_of
			( std::make_pair(1, 0.0174) )
			( std::make_pair(2, 0.0174) )
			( std::make_pair(3, 0.0686) )
			( std::make_pair(4, 0.0690) )
			( std::make_pair(5, 0.1256) )
			( std::make_pair(6, 0.1265) )
			( std::make_pair(7, -0.1655) )
			( std::make_pair(8, -0.1664) )
			( std::make_pair(9, 0.1257) )
			( std::make_pair(10, 0.1265) )
			( std::make_pair(11, 0.0687) )
			( std::make_pair(12, 0.0689) )
			( std::make_pair(13, 0.0174) )
			( std::make_pair(14, 0.0174) )
			;

	std::vector<GTRIData::voltage_type> hoa_dc_silly =
		boost::assign::list_of
			( std::make_pair(15, -1.0) )
			;

	//data.rf_null( rf, to36, bariumdata, -850.3 + 969.5 );
	FEMData::TrapData trap_7 = data.rf_null( 
		hoa_rf, hoa_dc_1MHz, ytterbiumdata, 20 );
	FEMData::TrapData trap_9 = data.rf_null( 
		hoa_rf, hoa_dc_1MHz_9, ytterbiumdata, 80 );

	std::cout << "Trap null: " << trap_7.x << ", " << 
		trap_7.y << ", " << trap_7.z << std::endl;

	std::cout << "Trap frequencies:" << std::endl;
	for( size_t i = 0; i < 3; ++i ) {
		std::cout << "2pi*" << trap_7.w[i] << ": " <<
			trap_7.axes[i][0] << ", " << trap_7.axes[i][1] << ", " <<
			trap_7.axes[i][2] << std::endl;
	}

	trap_7.z = 17.5;
	trap_9.z = 82.5;

	FEMData::vector_type pos, str;
	pos[0] = trap_7.x;		pos[1] = trap_7.y;		pos[2] = trap_7.z;
	str[0] = trap_7.w[0];	str[1] = trap_7.w[1];	str[2] = trap_7.w[2];

	std::ofstream out( "out.txt" );
	for( size_t i = 0; i < 10; ++i ) {
		double scale = double(i) / 10.;
		pos[2] = scale*(trap_9.z - trap_7.z) + trap_7.z;
		std::vector<GTRIData::voltage_type> test;
		for( size_t j = 0; j < hoa_dc_1MHz.size(); ++j ) {
			if( j < 2 && pos[2] > 50. ) continue;
			if( j >= hoa_dc_1MHz.size()-2 && pos[2] < 50. ) continue;
			test.push_back( std::make_pair( hoa_dc_1MHz[j].first,
				hoa_dc_1MHz[j].second * (1.0 - scale) +
				hoa_dc_1MHz_9[j].second * scale ) );
		}

		data.find_trapping_potential( pos, str, hoa_rf, test,
			ytterbiumdata, pos[2] );

		std::cout << "Step: " << i << std::endl;
		if( pos[2] > 50. ) out << 0.0 << " " << 0.0 << " ";
		for( size_t p = 0; p < test.size(); ++p ) {
			std::cout << "Electrode: " << test[p].first << " -> ";
			std::cout << test[p].second << std::endl;
			out << test[p].second << " ";
		}
		if( pos[2] < 50. ) out << 0.0 << " " << 0.0;
		out << std::endl;

		std::cout << std::endl;
		FEMData::TrapData trap = data.rf_null( 
			hoa_rf, test, ytterbiumdata, pos[2] );

		std::cout << "Trap null: " << trap.x << ", " << 
			trap.y << ", " << trap.z << std::endl;

		std::cout << "Trap frequencies:" << std::endl;
		for( size_t i = 0; i < 3; ++i ) {
			std::cout << "2pi*" << trap.w[i] << ": " <<
				trap.axes[i][0] << ", " << trap.axes[i][1] << ", " <<
				trap.axes[i][2] << std::endl;
		}
		std::cout << std::endl;
	}
	/*
	void find_trapping_potential( 
		vector_type position, vector_type strength,
		std::vector<voltage_type>& rf, 
		std::vector<voltage_type>& dc_guess,
		RFData data, double z );
		*/
	return 0;
}


